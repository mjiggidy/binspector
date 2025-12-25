import typing, dataclasses, logging

from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSFrameViewConfig
from ..utils import gestures
from ..overlays import framemap, frameruler, manager

from . import painters
from .framescene import BSBinFrameScene
from .actions import BSFrameViewActions

DEFAULT_FRAME_VIEW_MARGINS = QtCore.QMarginsF(
	BSFrameViewConfig.GRID_UNIT_SIZE.width(),
	BSFrameViewConfig.GRID_UNIT_SIZE.height(),
	BSFrameViewConfig.GRID_UNIT_SIZE.width(),
	BSFrameViewConfig.GRID_UNIT_SIZE.height(),
)


@dataclasses.dataclass(frozen=True)
class BSBinFrameViewGridInfo:
	"""Grid info for drawing a BSBinFrameView"""

	unit_size       :QtCore.QSizeF
	unit_divisions  :QtCore.QPointF

	@property
	def unit_step(self) -> QtCore.QPointF:

		return QtCore.QPointF(
			self.unit_size.width() / self.unit_divisions.x(),
			self.unit_size.height() / self.unit_divisions.y()
		)


class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	sig_zoom_level_changed      = QtCore.Signal(int)
	sig_zoom_range_changed      = QtCore.Signal(object)
	sig_overlay_manager_changed = QtCore.Signal(object)
	sig_view_rect_changed       = QtCore.Signal(object)
	sig_scene_changed           = QtCore.Signal(object)

	def __init__(self, *args, frame_scene:BSBinFrameScene|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		# QGraphics init
		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
		self.setOptimizationFlags(
			QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing |
			QtWidgets.QGraphicsView.OptimizationFlag.DontSavePainterState
		)

		# Scrollbar init
		self.setVerticalScrollBarPolicy  (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setCornerWidget(QtWidgets.QSizeGrip(self))

		self._current_zoom       = 1.0
		self._zoom_range         = range(100)
		self._grid_info          = BSBinFrameViewGridInfo(unit_size=BSFrameViewConfig.GRID_UNIT_SIZE, unit_divisions=BSFrameViewConfig.GRID_DIVISIONS)

		self._anim_zoom_adjust   = QtCore.QPropertyAnimation(parent=self)
		self._timer_cursor_reset = QtCore.QTimer()

		# Zoomer
		self._anim_zoom_adjust.setTargetObject(self)
		self._anim_zoom_adjust.setPropertyName(QtCore.QByteArray.fromStdString("raw_zoom"))
		self._anim_zoom_adjust.setDuration(300) #ms
		self._anim_zoom_adjust.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)

		# Cursor Resetter
		self._timer_cursor_reset.setInterval(1_000)  # ms
		self._timer_cursor_reset.setSingleShot(True)

		# Actions
		self._actions = BSFrameViewActions(self)

		# Background Painter
		# NOTE: Watches the QGraphicsView for palette changes (`parent=self`), NOT the viewport().
		# Viewport doesn't fire paletteChange events here.  Dunno. Maybe a TODO in disguise lol
		self._background_painter = painters.BSBinFrameBackgroundPainter(parent=self, grid_info=self._grid_info)
		self._item_brushes       = painters.BSFrameItemBrushManager(parent=self)

		# Doers of things
		# NOTE: Most of these fellers install themselves as eventFilters, enable mouse tracking on the widget, etc
		self._overlay_manager    = manager.BSGraphicsOverlayManager(parent=self.viewport())
		self._overlay_ruler      = frameruler.BSFrameRulerOverlay()
		self._overlay_map        = framemap.BSThumbnailMapOverlay()

		self._pinchy_boy         = gestures.BSPinchEventFilter(parent=self.viewport())
		self._pan_man            = gestures.BSPanEventFilter(parent=self.viewport())
		self._wheelzoom          = gestures.BSWheelZoomEventFilter(parent=self.viewport(), modifier_keys=QtCore.Qt.KeyboardModifier.AltModifier)

		self._overlay_map.setThumbnailOffset(self.viewport().rect().topRight())

		self._overlay_map._setEnabled(False)
		self._overlay_ruler._setEnabled(False)
		self._background_painter.setEnabled(False)

		self._overlay_manager.installOverlay(self._overlay_ruler)
		self._overlay_manager.installOverlay(self._overlay_map)

		# Actions

		self.addActions(self._actions.navigationActions().actions())
		self.addActions(self._actions.overlayActions().actions())

		#self._actions.act_toggle_grid               .setChecked(self._background_painter.isEnabled())
		#self._actions.act_toggle_ruler              .setChecked(self._overlay_ruler.isEnabled())
		#self._actions.act_toggle_map                .setChecked(self._overlay_map.isEnabled())
		
		self._actions.act_zoom_in.triggered         .connect(lambda: self.zoomIncrement())
		self._actions.act_zoom_out.triggered        .connect(lambda: self.zoomDecrement())
		
		# Action to Overlay
		self._actions.act_toggle_ruler.toggled      .connect(self._overlay_ruler._setEnabled)
		self._actions.act_toggle_map.toggled        .connect(self._overlay_map._setEnabled)
		self._actions.act_toggle_grid.toggled       .connect(self._background_painter.setEnabled)

		# Overlay to Action
		self._overlay_map.sig_enabled_changed       .connect(self._actions.act_toggle_map.setChecked)
		self._overlay_ruler.sig_enabled_changed     .connect(self._actions.act_toggle_ruler.setChecked)
		self._background_painter.sig_enabled_changed.connect(self._actions.act_toggle_grid.setChecked)


		# Manager signals
		
		self._overlay_map.sig_view_reticle_panned   .connect(self.centerOn)
		self._background_painter.sig_enabled_changed.connect(self.viewport().update)

		self._pan_man.sig_user_pan_started          .connect(self.beginPan)
		self._pan_man.sig_user_pan_moved            .connect(self.panViewByDelta)
		self._pan_man.sig_user_pan_finished         .connect(self.finishPan)

		self._pinchy_boy.sig_user_pinch_started     .connect(self._anim_zoom_adjust.stop)
		self._pinchy_boy.sig_user_pinch_moved       .connect(self.zoomViewByDelta)
		self._pinchy_boy.sig_user_pinch_finished    .connect(self.userFinishedPinch)

		self._wheelzoom.sig_user_zoomed             .connect(self.zoomByWheel)
		self._timer_cursor_reset.timeout            .connect(self.unsetCursor)

		# Misc signals

		self.horizontalScrollBar().valueChanged     .connect(self.handleVisibleSceneRectChanged)
		self.verticalScrollBar().valueChanged       .connect(self.handleVisibleSceneRectChanged)

		self.setScene(frame_scene or BSBinFrameScene(brushes_manager=self._item_brushes))

	def actions(self) -> BSFrameViewActions:
		"""Get the actions manager for the frame view"""

		return self._actions

	def setScene(self, scene:BSBinFrameScene):
		"""Override of `super().setScene()` with signals and cool stuff"""

		if self.scene() == scene:
			return

		if self.scene():
			self.scene().disconnect(self)

		scene.changed.connect(self.updateViewableSceneRect)
		#self.sceneRect.connect(lambda: self._overlay_map.setSceneRect)
		#scene.sig_bin_item_added.connect(self.updateThumbnails)

		super().setScene(scene)
#		self.setSceneRect(
#			scene.itemsBoundingRect().marginsAdded(DEFAULT_FRAME_VIEW_MARGINS)
#		)
		self.sig_scene_changed.emit(scene)

	@QtCore.Slot()
	def updateViewableSceneRect(self):
		
		self.setSceneRect(self.scene().itemsBoundingRect().marginsAdded(DEFAULT_FRAME_VIEW_MARGINS))
		self._overlay_map.setSceneRect(self.sceneRect())
		self._overlay_map.setThumbnailRects([item.sceneBoundingRect() for item in self.scene().items()]) # NOTE: Too expensive lol
		#self.updateThumbnails()



	#@QtCore.Slot()
	#def updateThumbnails(self):
	#	self._overlay_map.setThumbnailRects([item.sceneBoundingRect() for item in self.scene().items()])


	@QtCore.Slot()
	def handleVisibleSceneRectChanged(self):
		"""Do necessary updates when user pans/zooms"""

		self.updateRulerTicks()

		self._overlay_map.setViewReticle(self.visibleSceneRect())

		self.sig_view_rect_changed.emit(self.visibleSceneRect())

	def setTransform(self, matrix:QtGui.QTransform, *args, combine:bool=False, **kwargs) -> None:

		super().setTransform(matrix, combine)
		self.handleVisibleSceneRectChanged()

	def overlayManager(self) -> manager.BSGraphicsOverlayManager:

		return self._overlay_manager

	@QtCore.Slot(object)
	def setOverlayManager(self, overlay_manager:manager.BSGraphicsOverlayManager):

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

		self._timer_cursor_reset.stop()
		self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

	@QtCore.Slot(QtCore.QPoint)
	def panViewByDelta(self, pan_delta:QtCore.QPoint):

		self._timer_cursor_reset.stop()
		self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - pan_delta.x())
		self.verticalScrollBar()  .setValue(self.verticalScrollBar()  .value() - pan_delta.y())

	@QtCore.Slot()
	def finishPan(self):

		self._timer_cursor_reset.start()
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

		self._anim_zoom_adjust.stop()
		self._anim_zoom_adjust.setStartValue(start_val)
		self._anim_zoom_adjust.setEndValue(end_val)
		self._anim_zoom_adjust.start()

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

		# NOTE:  See Background drawing code for better coordinate alignment, gonna wanna roll that all in 

		if QtCore.Qt.Orientation.Horizontal in tick_orientations:

			# Align to grid divisions
			range_scene_start = rect_scene.left()  - rect_scene.left()  % self._grid_info.unit_size.width()
			range_scene_end  = rect_scene.right()  - rect_scene.right() % self._grid_info.unit_size.width() + self._grid_info.unit_size.width()
			range_scene_steps = (range_scene_end - range_scene_start) / self._grid_info.unit_size.width() + 1

			ticks = []

			for step in range(round(range_scene_steps)):

				scene_x = range_scene_start + (self._grid_info.unit_size.width() * step)
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
			range_scene_start = rect_scene.top() - rect_scene.top() % self._grid_info.unit_size.height()
			range_scene_end   = rect_scene.bottom() - rect_scene.bottom() % self._grid_info.unit_size.height() + self._grid_info.unit_size.height()
			range_scene_steps = (range_scene_end - range_scene_start) / self._grid_info.unit_size.height() + 1

			ticks = []

			for step in range(round(range_scene_steps)):

				scene_y = range_scene_start + (self._grid_info.unit_size.height() * step)
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

		super().drawBackground(painter, rect)

		self._background_painter.drawBackground(painter, rect)

#	def drawForeground(self, painter, rect):
		#  NOTE Just because I keep forgetting and trying it: drawForeground is not suitable for
		#  drawing overlays because the painter is scaled to scene coords and it's a whole thing.

	def drawOverlays(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		self._overlay_manager.paintOverlays(painter, self.viewport().rect())

	def paintEvent(self, event):
		"""Paint widget, then overlays"""

		super().paintEvent(event)

		painter = QtGui.QPainter(self.viewport())
		try:
			self.drawOverlays(painter, self.viewport().rect())
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing overlays: %s", e)
		finally:
			painter.end()

	def resizeEvent(self, event):

		self.handleVisibleSceneRectChanged()
		return super().resizeEvent(event)
	
	def mousePressEvent(self, event:QtGui.QMouseEvent):

		if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
			
			# Handle super() first so items are selected
			ret = super().mousePressEvent(event)
			self.scene().raiseItemsToTop(self.scene().selectedItems())
			return ret
		
		return super().mousePressEvent(event)