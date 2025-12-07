from PySide6 import QtCore, QtGui
from . import abstractoverlay

DEFAULT_DISPLAY_SIZE      = QtCore.QSizeF(200, 300)
DEFAULT_DISPLAY_MARGINS   = QtCore.QMarginsF(50, 40, 26, 36)
DEFAULT_DISPLAY_ALIGNMENT = QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignRight
DEFAULT_DISPLAY_OFFSET    = QtCore.QPointF(50,50)

class BSFrameMapOverlay(abstractoverlay.BSAbstractOverlay):
	"""A thumbnail map overlay thing"""

	sig_map_display_alignment_changed = QtCore.Signal(QtCore.Qt.AlignmentFlag)
	sig_display_position_changed      = QtCore.Signal(QtCore.QPointF)
	sig_display_size_changed          = QtCore.Signal(QtCore.QSizeF)
	sig_scene_rect_changed            = QtCore.Signal(QtCore.QRectF)
	sig_visible_recticle_changed      = QtCore.Signal(QtCore.QRectF)


	def __init__(self,
		*args,
		display_size:   QtCore.QSize|QtCore.QSizeF|None = None,
		display_align:  QtCore.Qt.AlignmentFlag|None    = None,
		display_offset: QtCore.QPointF|None             = None,
		display_margin: QtCore.QMarginsF|None           = None,
		scene_rect:     QtCore.QRectF|None              = None,
		view_rect:      QtCore.QRectF|None              = None,
		**kwargs):

		super().__init__(*args, **kwargs)

		self._map_display_size    = display_size   or DEFAULT_DISPLAY_SIZE
		self._map_display_offset  = display_offset or DEFAULT_DISPLAY_OFFSET
		self._map_display_margins = display_margin or DEFAULT_DISPLAY_MARGINS
		self._map_display_align   = display_align  or DEFAULT_DISPLAY_ALIGNMENT

		
		self._rect_scene   = scene_rect or QtCore.QRectF(-500,-500,1000,1000)
		self._rect_reticle = view_rect  or self._rect_scene
		
		self._scene_to_display_transform = QtGui.QTransform()
		"""Transform scene coordinate rects to viewport coordinate rects"""

		self._mouse_drag_start   = QtCore.QPointF()

		self._setupSceneToDisplayTransform()
	
	def _setupSceneToDisplayTransform(self, rect_canvas:QtCore.QRectF|None = None):
		"""Build the transform to map scene coordinates to thumbnail coordinates"""

		if self._rect_scene.isNull():

			self._scene_to_display_transform = QtGui.QTransform()
			return
		
		rect_canvas = rect_canvas or self.widget().rect()

		transform = QtGui.QTransform()

		#"RECT CANVAS: ", rect_canvas)

		# Scale to thumbnail display size
		rect_scene = QtCore.QRectF(self._rect_scene)
		scale_factor = self._map_display_size.width() / rect_scene.width()
		transform.scale(scale_factor, scale_factor)
		
		# Offset scene so topLeft point is (0,0)
		transform.translate(rect_canvas.left() - self._rect_scene.left(), rect_canvas.top() - self._rect_scene.top())
		
		# NOTE: Preferring width for now I suppose



		# Offset for alignment
		self._scene_to_display_transform = transform


		#print("*******MAPPED", transform.mapRect(self._rect_scene))

		# Offset for margins

		# Offset for user position
		transform.translate(self._map_display_offset.x(), self._map_display_offset.y())
	
	def sceneRect(self) -> QtCore.QRectF:
		"""The scene rect, in scene coordinates"""

		return self._rect_scene
	
	@QtCore.Slot(QtCore.QRectF)
	def setVisibleRecticle(self, visible_rect:QtCore.QRectF):
		"""Set the visible reticle. Relative to sceneRect!"""

		if self._rect_reticle != visible_rect:

			old_rect = self.thumbnailDisplayRect()
			self.update(old_rect)

			self._rect_reticle = visible_rect
			self.sig_visible_recticle_changed.emit(visible_rect)

			self.update(visible_rect)

	def viewRecticle(self) -> QtCore.QRectF:
		"""The visible reticle, in scene coordinates"""

		return self._rect_reticle
	
	@QtCore.Slot(QtCore.QRectF)
	def setSceneRect(self, scene_rect:QtCore.QRectF):

		if self._rect_scene != scene_rect:

			old_rect = self.thumbnailDisplayRect()
			self.update(old_rect)

			self._rect_scene = scene_rect
			self.sig_scene_rect_changed.emit(scene_rect)

			self._setupSceneToDisplayTransform()

			self.update(self.thumbnailDisplayRect())
	
	def sceneRect(self) -> QtCore.QRectF:
		"""The scene rect, in scene coordinates"""

		return self._rect_scene
	
	def thumbnailDisplayRect(self, rect_canvas:QtCore.QRectF|None=None) -> QtCore.QRectF:
		"""The scene rect, scaled and positioned to its display dimensions relative to the canvas"""

		rect_canvas = rect_canvas or self.widget().rect()

		return self._scene_to_display_transform.mapRect(self._rect_scene)
	
	def reticleDisplayRect(self, rect_canvas:QtCore.QRectF|None=None) -> QtCore.QRectF:
		"""The reticle rect, scaled and positioned to its display dimentions relative to the canvas"""

		rect_canvas = rect_canvas or self.widget().rect()

		return self._scene_to_display_transform.mapRect(self._rect_reticle)
	
	@QtCore.Slot(QtCore.QSizeF)
	def setDisplaySize(self, display_size:QtCore.QSizeF):
		"""Size of the thumbnail map display rect thing, in widget coordinates"""

		if not self._map_display_size == display_size:
			
			old_rect = self.thumbnailDisplayRect()
			self.update(old_rect)
			
			self._map_display_size = display_size
			self.sig_display_size_changed.emit(display_size)

			self._setupSceneToDisplayTransform()

			new_rect = self.thumbnailDisplayRect()
			self.update(new_rect)
		
	def displaySize(self) -> QtCore.QSizeF:
		"""Size of the thumbnail map display rect thing, in widget coordinates"""

		return self._map_display_size

	@QtCore.Slot(QtCore.Qt.AlignmentFlag)
	def setMapDisplayAlignment(self, display_align:QtCore.Qt.AlignmentFlag):
		"""Anchored alignment in the parent widget"""

		if not self._map_display_align == display_align:

			old_rect = self.thumbnailDisplayRect()
			self.update(old_rect)

			self._map_display_align = display_align
			self.sig_map_display_alignment_changed.emit(display_align)

			new_rect = self.thumbnailDisplayRect()
			self.update(self.thumbnailDisplayRect(new_rect))

	def mapDisplayAlignment(self) -> QtCore.Qt.AlignmentFlag:
		"""Alignment to the parent widget"""

		return self._map_display_align
	
	@QtCore.Slot(QtCore.QPointF)
	def setDisplayPositionOffset(self, position_offset:QtCore.QPointF):

		if self._map_display_offset != position_offset:

			old_rect = self.thumbnailDisplayRect()
			self.update(old_rect)

			self._map_display_offset += position_offset
			self.sig_display_position_changed.emit(position_offset)

			self._setupSceneToDisplayTransform()

			new_rect = self.thumbnailDisplayRect()
			self.update(new_rect)

	def positionOffset(self) -> QtCore.QPointF:
		"""Position offset from aligned anchor"""

		return self._map_display_offset

	def paintOverlay(self, painter, rect_canvas):
		"""Do the paint"""

		rect_canvas = rect_canvas or self.widget().rect()

		self._draw_frame(painter, rect_canvas)
		self._draw_view_reticle(painter, rect_canvas)


	############
	# Draw Logic
	############

	def _draw_frame(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF|None=None):

		rect_canvas = rect_canvas or self.widget().rect()
		rect_frame = self.thumbnailDisplayRect(rect_canvas)

		brush = self._palette.window()
		pen   = QtGui.QPen(self._palette.windowText().color())
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		pen.setWidthF(3)

		painter.setBrush(brush)
		painter.setPen(pen)

		#print("**DRAW FRAME:", rect_frame)

		painter.drawRect(rect_frame)
		#painter.drawRect(rect_canvas)
	
	def _draw_view_reticle(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF|None=None):

		rect_canvas = rect_canvas or self.widget().rect()
#		
		rect_reticle = self.reticleDisplayRect(rect_canvas)
		painter.drawRect(rect_reticle)


	#############
	# Mouse Stuff
	#############
	
	def _dragIsActive(self) -> bool:
		"""User is currently dragging"""

		return not self._mouse_drag_start.isNull()

	def beginUserDragDisplayRect(self, drag_start_position:QtCore.QPointF) -> bool:
		
		# Start position relative to the top left corner of the display rect
		self._mouse_drag_start = drag_start_position - self.thumbnailDisplayRect().topLeft()
		self.update(self.thumbnailDisplayRect())

		return True
	
	def updateUserDragDisplayRect(self, drag_update_position:QtCore.QPointF) -> bool:

		if not self._dragIsActive():
			return False
		
		drag_update_position = drag_update_position - self._mouse_drag_start - self.thumbnailDisplayRect().topLeft()

		#print(drag_update_position)
		#drag_update_position -= self.thumbnailDisplayRect().topLeft() + self._mouse_drag_start

		
		# self.setDisplayPositionOffset calls update()
		self.setDisplayPositionOffset(drag_update_position)

		return True
	
	def endUserDragDisplayRect(self) -> bool:

		self._mouse_drag_start = QtCore.QPointF()
		self.update(self.thumbnailDisplayRect())
		return True
	
	def event(self, event):

		if event.type() == QtCore.QEvent.Type.MouseButtonPress:
			
			if not self.thumbnailDisplayRect(self.widget().rect()).contains(event.position()):
				return False
			
			if event.buttons() & QtCore.Qt.MouseButton.LeftButton and event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
				return self.beginUserDragDisplayRect(event.position())
			
			return True
		
		elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._dragIsActive():
			return self.endUserDragDisplayRect()
		
		elif event.type() == QtCore.QEvent.Type.MouseMove:

			if self._dragIsActive():
				return self.updateUserDragDisplayRect(event.position())

		elif event.type() == QtCore.QEvent.Type.Resize:
			self.update(self.widget().rect())

		return super().event(event)
	
