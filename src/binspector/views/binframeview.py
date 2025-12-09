import logging, typing
from PySide6 import QtCore, QtGui, QtWidgets
from ..managers import eventfilters, overlaymanager
from ..models import viewmodels, sceneitems
from ..overlays import frameruler, framemap

GRID_DIVISIONS     = 3
GRID_UNIT_SIZE     = QtCore.QSizeF(18,12)

class BSBinFrameScene(QtWidgets.QGraphicsScene):
	"""Graphics scene based on a bin model"""

	DEFAULT_ITEM_FLAGS = \
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable|\
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|\
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable

	sig_bin_filter_model_changed   = QtCore.Signal(object)
	sig_selection_model_changed    = QtCore.Signal(object)
	sig_bin_item_added             = QtCore.Signal(object)

	def __init__(self, *args, bin_filter_model:viewmodels.LBTimelineViewModel|None=None, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._bin_filter_model = bin_filter_model or viewmodels.LBSortFilterProxyModel()
		self._selection_model  = QtCore.QItemSelectionModel()
		
		self._bin_items:list[sceneitems.BSFrameModeItem] = list()

		self._setupModel()
		self._setupSelectionModel()

	def _setupModel(self):

		self._bin_filter_model.rowsInserted  .connect(self.addBinItems)
		self._bin_filter_model.rowsAboutToBeRemoved .connect(self.removeBinItems)
		self._bin_filter_model.modelReset    .connect(self.clear)
		
		self._bin_filter_model.rowsMoved     .connect(self.reloadBinFilterModel)
		self._bin_filter_model.layoutChanged .connect(self.reloadBinFilterModel)

		self.selectionChanged.connect(self.updateSelectionModel)

	def _setupSelectionModel(self):
		self._selection_model.selectionChanged.connect(self.setSelectedItemsFromSelectionModel)

	def selectionModel(self) -> QtCore.QItemSelectionModel:
		return self._selection_model
	
	@QtCore.Slot(object)
	def setSelectionModel(self, selection_model:QtCore.QItemSelectionModel):

		if self._selection_model != selection_model:

			self._selection_model.disconnect(self)
			
			self._selection_model = selection_model
			self._setupSelectionModel()
			self.sig_selection_model_changed.emit(selection_model)


	@QtCore.Slot(object,object)
	def setSelectedItemsFromSelectionModel(self, selected:QtCore.QItemSelection, deselected:QtCore.QItemSelection):
		"""Update selected bin items according to the selection model"""

		#self._selection_model.blockSignals(True)

		for row in set(i.row() for i in selected.indexes()):
			item = self._bin_items[row]
			if not item.isSelected():
				self._bin_items[row].setSelected(True)
			
		for row in set(i.row() for i in deselected.indexes()):
			item = self._bin_items[row]
			if item.isSelected():
				self._bin_items[row].setSelected(False)

		#self._selection_model.blockSignals(False)

	@QtCore.Slot()
	def updateSelectionModel(self):
		"""Update selection model to mirror the scene's selected items"""

		current_rows = set(self._bin_items.index(i) for i in self.selectedItems())
		stale_rows   = set(i.row() for i in self._selection_model.selection().indexes()) - current_rows

		
		self.blockSignals(True)
		
		self._selection_model.clear()
		
		for row in current_rows:
		
			self._selection_model.select(
				self._bin_filter_model.index(row, 0, QtCore.QModelIndex()),
				QtCore.QItemSelectionModel.SelectionFlag.Select|
				QtCore.QItemSelectionModel.SelectionFlag.Rows
			)

		self.blockSignals(False)

	def binFilterModel(self) -> viewmodels.LBSortFilterProxyModel:
		return self._bin_filter_model

	@QtCore.Slot(object)
	def setBinFilterModel(self, bin_model:viewmodels.LBSortFilterProxyModel):
		
		if not self._bin_filter_model == bin_model:

			self._bin_filter_model.disconnect(self)

			self._bin_filter_model = bin_model
			self._setupModel()

			logging.getLogger(__name__).debug("Set bin filter model=%s (source model=%s)", self._bin_filter_model, self._bin_filter_model.sourceModel())
			self.sig_bin_filter_model_changed.emit(bin_model)

	@QtCore.Slot()
	def reloadBinFilterModel(self):
		"""Reset and reload items from bin filter model to stay in sync with order changes"""
		
		logging.getLogger(__name__).debug("About to clear bin frame view for layout change")
		self.clear()

		self.addBinItems(QtCore.QModelIndex(), 0, self._bin_filter_model.rowCount()-1)
		#self.setSelectedItemsFromSelectionModel(self._selection_model.selection(), QtCore.QItemSelection())
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def addBinItems(self, parent_row_index:QtCore.QModelIndex, row_start:int, row_end:int):

		for row in range(row_start, row_end+1):

			# Resolve source model to ensure we always have relevent columns available
			proxy_row_index  = self._bin_filter_model.index(row, 0, parent_row_index)
			#parent_row_index = self._bin_filter_model.mapToSource(proxy_row_index)
			
			bin_item_name = proxy_row_index.data(viewmodels.BSBinItemDataRoles.BSItemName)
			bin_item_coords = proxy_row_index.data(viewmodels.BSBinItemDataRoles.BSFrameCoordinates)

			#bin_item_name = self._bin_filter_model.index(row, 2, parent_index).data(QtCore.Qt.ItemDataRole.DisplayRole)

			bin_item = sceneitems.BSFrameModeItem()
			bin_item.setName(str(bin_item_name))
			bin_item.setFlags(self.DEFAULT_ITEM_FLAGS)

			x, y = bin_item_coords
			bin_item.setPos(QtCore.QPoint(x, y))

			self._bin_items.insert(row, bin_item)


			self.addItem(bin_item)
	
			self.sig_bin_item_added.emit(bin_item)

	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def removeBinItems(self, model_index:QtCore.QModelIndex, row_start:int, row_end:int):
		
		for row in range(row_end, row_start-1, -1):

			bin_item = self._bin_items.pop(row)
			self.removeItem(bin_item)
	
	@QtCore.Slot()
	def clear(self):
		
		self._bin_items.clear()
		logging.getLogger(__name__).debug("Bin frame view cleared")
		return super().clear()



class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	sig_zoom_level_changed      = QtCore.Signal(int)
	sig_zoom_range_changed      = QtCore.Signal(object)
	sig_overlay_manager_changed = QtCore.Signal(object)
	sig_view_rect_changed       = QtCore.Signal(object)
	sig_scene_changed           = QtCore.Signal(object)

	def __init__(self, *args, frame_scene:BSBinFrameScene|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
		
		

		self._current_zoom = 1.0
		self._zoom_range   = range(100)
		
		# NOTE: Since just the overlaymanager needs mouse tracking, OverlayManger sets it when it installs itself as the parent
		#self.viewport().setMouseTracking(True)
		
		# Install overlay manager on the viewport widget
		self._overlay_manager = overlaymanager.BSGraphicsOverlayManager(parent=self.viewport())
		
		self._overlay_ruler = frameruler.BSFrameRulerOverlay()
		self._overlay_map   = framemap.BSThumbnailMapOverlay()
		self._overlay_manager.installOverlay(self._overlay_ruler)
		self._overlay_manager.installOverlay(self._overlay_map)

		# NOTE: These install themselves as eventFilters now during __init__()
		self._pinchy_boy   = eventfilters.BSPinchEventFilter(parent=self.viewport())
		self._pan_man      = eventfilters.BSPanEventFilter(parent=self.viewport())
		self._wheelzoom    = eventfilters.BSWheelZoomEventFilter(parent=self.viewport(), modifier_keys=QtCore.Qt.KeyboardModifier.AltModifier)

		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

		self._act_zoom_in  = QtGui.QAction("Zoom In")
		self._act_zoom_in.triggered.connect(lambda: self.zoomIncrement())
		self._act_zoom_in.setShortcut(QtGui.QKeySequence.StandardKey.ZoomIn)
		self._act_zoom_in.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ZoomIn))

		self._act_zoom_out  = QtGui.QAction("Zoom Out")
		self._act_zoom_out.triggered.connect(lambda: self.zoomDecrement())
		self._act_zoom_out.setShortcut(QtGui.QKeySequence.StandardKey.ZoomOut)
		self._act_zoom_out.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ZoomOut))

		self._act_toggle_ruler = QtGui.QAction("Toggle Ruler")
		self._act_toggle_ruler.setCheckable(True)
		self._act_toggle_ruler.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier| QtCore.Qt.Key.Key_R))
		self._act_toggle_ruler.toggled.connect(self._overlay_ruler._setEnabled)

		self._act_toggle_map  = QtGui.QAction("Toggle Bin Map")
		self._act_toggle_map.setCheckable(True)
		self._act_toggle_map.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_M))
		self._act_toggle_map.toggled.connect(self._overlay_map._setEnabled)

		self.addAction(self._act_zoom_in)
		self.addAction(self._act_zoom_out)
		
		self.addAction(self._act_toggle_ruler)
		self.addAction(self._act_toggle_map)

		self._overlay_ruler._setEnabled(self._act_toggle_ruler.isChecked())
		self._overlay_map._setEnabled(self._act_toggle_map.isChecked())

		self._zoom_animator = QtCore.QPropertyAnimation(parent=self)
		self._zoom_animator.setTargetObject(self)
		self._zoom_animator.setPropertyName(QtCore.QByteArray.fromStdString("raw_zoom"))
		self._zoom_animator.setDuration(300) #ms
		self._zoom_animator.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)

		# Pan Hand Cursor Timer
		self._pan_cursor_timer = QtCore.QTimer()
		self._pan_cursor_timer.setInterval(1_000) # ms
		self._pan_cursor_timer.setSingleShot(True)
		self._pan_cursor_timer.timeout.connect(self.unsetCursor)

		self._pan_man.sig_user_pan_started.connect(self.beginPan)
		self._pan_man.sig_user_pan_moved.connect(self.panViewByDelta)
		self._pan_man.sig_user_pan_finished.connect(self.finishPan)

		self._pinchy_boy.sig_user_pinch_started .connect(self._zoom_animator.stop)
		self._pinchy_boy.sig_user_pinch_moved   .connect(self.zoomViewByDelta)
		self._pinchy_boy.sig_user_pinch_finished.connect(self.userFinishedPinch)

		self._wheelzoom.sig_user_zoomed.connect(self.zoomByWheel)

		self._overlay_map.sig_view_reticle_panned.connect(self.centerOn)

		

		self.horizontalScrollBar().valueChanged.connect(self.handleVisibleSceneRectChanged)
		self.verticalScrollBar().valueChanged.connect(self.handleVisibleSceneRectChanged)
		
		self.setScene(frame_scene or BSBinFrameScene())
		

		

	def setScene(self, scene:BSBinFrameScene):
		
		if not self.scene() == scene:
			
			#self.scene().sceneRectChanged.disconnect(self._overlay_map)

			if self.scene():
				self.scene().disconnect(self)


			scene.sceneRectChanged.connect(self._overlay_map.setSceneRect)
			scene.sig_bin_item_added.connect(self.updateThumbnails)
			
			super().setScene(scene)

			self._overlay_map.setSceneRect(scene.sceneRect())

			region = QtGui.QRegion()

			for item in scene.items():
				#print(item.boundingRect())
				region.united(item.sceneBoundingRect())
			
			#self._overlay_map.setThumbnails(region)

			self.sig_scene_changed.emit(scene)

	@QtCore.Slot()
	def updateThumbnails(self):

		self._overlay_map.setThumbnailRects([item.sceneBoundingRect() for item in self.scene().items()])

	@QtCore.Slot()
	def handleVisibleSceneRectChanged(self):
		"""Do necessary updates when user pans/zooms"""

		self.updateRulerTicks()

		self._overlay_map.setViewReticle(self.visibleSceneRect())

		self.sig_view_rect_changed.emit(self.visibleSceneRect())

	def setTransform(self, matrix:QtGui.QTransform, *args, combine:bool=False, **kwargs) -> None:

		super().setTransform(matrix, combine)
		self.handleVisibleSceneRectChanged()

	def overlayManager(self) -> overlaymanager.BSGraphicsOverlayManager:

		return self._overlay_manager
	
	@QtCore.Slot(object)
	def setOverlayManager(self, overlay_manager:overlaymanager.BSGraphicsOverlayManager):

		if self._overlay_manager != overlay_manager:
			
			self._overlay_manager = overlay_manager
			self.sig_overlay_manager_changed.emit(overlay_manager)


	def scene(self) -> BSBinFrameScene:
		# Just for type hints
		return super().scene()

	@QtCore.Slot(int, QtCore.Qt.Orientation)
	def zoomByWheel(self, zoom_delta:int, orientation:QtCore.Qt.Orientation):

		if zoom_delta > 0:
			self.zoomIncrement(1)
		elif zoom_delta < 0:
			self.zoomIncrement(-1)
		else:
			logging.getLogger(__name__).debug("Ignored weird 0-delta zoom")
	
	@QtCore.Slot()
	@QtCore.Slot(int)
	def zoomIncrement(self, zoom_step:int=1):

		zoom_step += self._current_zoom

		self.setZoom(
			max(
				self._zoom_range.start,
				min(
					zoom_step,
					self._zoom_range.stop
				)
			)
		)
	
	@QtCore.Slot()
	@QtCore.Slot(int)
	def zoomDecrement(self, zoom_step:int=1):
		
		return self.zoomIncrement(-zoom_step)

	@QtCore.Slot()
	def beginPan(self):

		self._pan_cursor_timer.stop()
		self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
	
	@QtCore.Slot(QtCore.QPoint)
	def panViewByDelta(self, pan_delta:QtCore.QPoint):

		self._pan_cursor_timer.stop()
		self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - pan_delta.x())
		self.verticalScrollBar()  .setValue(self.verticalScrollBar()  .value() - pan_delta.y())
	
	@QtCore.Slot()
	def finishPan(self):

		self._pan_cursor_timer.start()
		self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

	@QtCore.Slot(float)
	def zoomViewByDelta(self, zoom_delta:float):
		
		zoom_delta += 1
		new_zoom = self._current_zoom * (zoom_delta)

		# Allow overshoot
		ZOOM_RANGE_OVERSHOOT = range(self._zoom_range.start-1, self._zoom_range.stop +1)
		padded_zoom = max(
			ZOOM_RANGE_OVERSHOOT.start,
			min(
				new_zoom,
				ZOOM_RANGE_OVERSHOOT.stop
			)
		)

		self.setZoom(padded_zoom)

	@QtCore.Slot()
	def userFinishedPinch(self):

		start_val = self._current_zoom
		end_val = max(self._zoom_range.start, min(round(self._current_zoom), self._zoom_range.stop))

		if start_val == end_val:
			#print("EXACT")
			return

		self._zoom_animator.stop()
		self._zoom_animator.setStartValue(start_val)
		self._zoom_animator.setEndValue(end_val)
		self._zoom_animator.start()

	@QtCore.Slot(object)
	def setZoomRange(self, zoom_range:range):

		if self._zoom_range != zoom_range:
			self._zoom_range = zoom_range
			self.sig_zoom_range_changed.emit(zoom_range)
	
	def zoomRange(self) -> range:
		return self._zoom_range
	
	@QtCore.Property(float)
	def raw_zoom(self) -> float:

		return self._current_zoom
	
	@raw_zoom.setter
	def raw_zoom(self, raw_zoom:float):

		#print(raw_zoom)

		if raw_zoom != self._current_zoom:
			self._current_zoom = raw_zoom
			
			t = QtGui.QTransform()
			t.scale(raw_zoom, raw_zoom)
			self.setTransform(t)

			self.sig_zoom_level_changed.emit(raw_zoom)

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setZoom(self, zoom_level:int|float):

		if zoom_level != self._current_zoom:

			zoom_level = float(zoom_level) #/ float(4)
			self._current_zoom = zoom_level

			t = QtGui.QTransform()
			t.scale(zoom_level, zoom_level)
			self.setTransform(t)

			self.sig_zoom_level_changed.emit(zoom_level)

			self.handleVisibleSceneRectChanged()

	def updateRulerTicks(self, rect_scene:QtCore.QRect|None=None, tick_orientations:typing.Iterable[QtCore.Qt.Orientation]|None=None):

		rect_scene        = rect_scene or self.visibleSceneRect()
		tick_orientations = tick_orientations or [QtCore.Qt.Orientation.Horizontal, QtCore.Qt.Orientation.Vertical]

		if QtCore.Qt.Orientation.Horizontal in tick_orientations:
			
			# Align to grid divisions
			range_scene_start = rect_scene.left()  - rect_scene.left()  % GRID_UNIT_SIZE.width()
			range_scene_end  = rect_scene.right()  - rect_scene.right() % GRID_UNIT_SIZE.width() + GRID_UNIT_SIZE.width()
			range_scene_steps = (range_scene_end - range_scene_start) / GRID_UNIT_SIZE.width() + 1

			ticks = []
			
			for step in range(round(range_scene_steps)):

				scene_x = range_scene_start + (GRID_UNIT_SIZE.width() * step)
				viewport_x = self.mapFromScene(scene_x, 0).x()

				ticks.append(
					frameruler.BSRulerTickInfo(
						ruler_offset = viewport_x,
						tick_label = str(round(scene_x))
					)
				)

			self._overlay_ruler.setTicks(ticks, QtCore.Qt.Orientation.Horizontal)
		
		if QtCore.Qt.Orientation.Vertical in tick_orientations:

			# Align to grid divisions
			range_scene_start = rect_scene.top() - rect_scene.top() % GRID_UNIT_SIZE.height()
			range_scene_end   = rect_scene.bottom() - rect_scene.bottom() % GRID_UNIT_SIZE.height() + GRID_UNIT_SIZE.height()
			range_scene_steps = (range_scene_end - range_scene_start) / GRID_UNIT_SIZE.height() + 1

			ticks = []

			for step in range(round(range_scene_steps)):

				scene_y = range_scene_start + (GRID_UNIT_SIZE.height() * step)
				viewport_y = self.mapFromScene(0, scene_y).y()

				ticks.append(
					frameruler.BSRulerTickInfo(
						ruler_offset= viewport_y,
						tick_label = str(round(scene_y))
					)
				)

			self._overlay_ruler.setTicks(ticks, QtCore.Qt.Orientation.Vertical)
	
	def visibleSceneRect(self) -> QtCore.QRectF:
		"""The portion of the scene rect viewable in the viewport"""

		return QtCore.QRectF(
			self.mapToScene(self.viewport().rect().topLeft()),
			self.mapToScene(self.viewport().rect().bottomRight()),
		)
	
	def drawBackground(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		pen_boundary = QtGui.QPen()
		pen_boundary.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen_boundary.setCosmetic(True)
		pen_boundary.setWidth(1)
		pen_boundary.setColor(self.parentWidget().palette().window().color())

		pen_division = QtGui.QPen()
		pen_division.setStyle(QtCore.Qt.PenStyle.DashLine)
		pen_division.setCosmetic(True)
		pen_division.setWidth(1)
		pen_division.setColor(self.parentWidget().palette().window().color())

		super().drawBackground(painter, rect)

		painter.save()

		# Setup stuff for ruler
		
		coord_font = self.font()
		painter.setFont(coord_font)

		for x in range(round(rect.left()), round(rect.right())+1):

			if x % (GRID_UNIT_SIZE.width() // GRID_DIVISIONS):
				continue

			if x % (GRID_UNIT_SIZE.width()) == 0:
				painter.setPen(pen_boundary)
			else:
				painter.setPen(pen_division)
			
			painter.drawLine(QtCore.QLine(
				QtCore.QPoint(x, rect.top()),
				QtCore.QPoint(x, rect.bottom())
			))
		
		for y in range(int(rect.top()), int(rect.bottom())+1):
			
			if y % (GRID_UNIT_SIZE.height() // GRID_DIVISIONS):
				continue

			if y % (GRID_UNIT_SIZE.height()) == 0:
				painter.setPen(pen_boundary)
			else:
				painter.setPen(pen_division)
			
			painter.drawLine(QtCore.QLine(
				QtCore.QPoint(rect.left(), y),
				QtCore.QPoint(rect.right(), y),
			))
			
		painter.restore()
	
	def paintEvent(self, event):
		"""Paint widget, then overlays"""

		super().paintEvent(event)

		painter = QtGui.QPainter(self.viewport())
		try:
			self._overlay_manager.paintOverlays(painter, self.viewport().rect())
		except Exception as e:
			logging.getLogger(__name__).error(e)
		finally:
			painter.end()
	
	def resizeEvent(self, event):
		self.handleVisibleSceneRectChanged()
		return super().resizeEvent(event)