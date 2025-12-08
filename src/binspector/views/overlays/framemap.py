from PySide6 import QtCore, QtGui
from . import abstractoverlay

DEFAULT_DISPLAY_SIZE      = QtCore.QSizeF(150, 150)
DEFAULT_DISPLAY_MARGINS   = QtCore.QMarginsF(32, 32, 32, 32)
DEFAULT_DISPLAY_ALIGNMENT = QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignRight
DEFAULT_DISPLAY_OFFSET    = QtCore.QPointF(32,32)

DEFAULT_KEY_DRAG_THUMBNAIL= QtCore.Qt.KeyboardModifier.AltModifier

class BSThumbnailMapOverlay(abstractoverlay.BSAbstractOverlay):
	"""A thumbnail map overlay thing"""

	sig_thumbnail_alignment_changed = QtCore.Signal(QtCore.Qt.AlignmentFlag)
	sig_thumbnail_position_changed  = QtCore.Signal(QtCore.QPointF)
	sig_thumbnail_size_changed      = QtCore.Signal(QtCore.QSizeF)
	sig_scene_rect_changed          = QtCore.Signal(QtCore.QRectF)
	sig_view_reticle_changed        = QtCore.Signal(QtCore.QRectF)

	sig_view_reticle_panned         = QtCore.Signal(QtCore.QPointF)
	"""New view rect in scene coordinates"""


	def __init__(self,
		*args,
		thumbnail_size:   QtCore.QSize|QtCore.QSizeF|None = None,
		thumbnail_align:  QtCore.Qt.AlignmentFlag|None    = None,
		thumbnail_offset: QtCore.QPointF|None             = None,
		display_margins:  QtCore.QMarginsF|None           = None,
		scene_rect:       QtCore.QRectF|None              = None,
		view_rect:        QtCore.QRectF|None              = None,
		**kwargs):

		super().__init__(*args, **kwargs)

		# Metrics
		self._thumb_display_size    = thumbnail_size   or DEFAULT_DISPLAY_SIZE
		self._thumb_display_offset  = thumbnail_offset or DEFAULT_DISPLAY_OFFSET
		self._thumb_display_margins = display_margins  or DEFAULT_DISPLAY_MARGINS
		self._thumb_display_align   = thumbnail_align  or DEFAULT_DISPLAY_ALIGNMENT

		self._thumbnails_path       = QtGui.QPainterPath()
		self._thumbnails_rects      = []

		# Source rects
		self._rect_scene   = scene_rect or QtCore.QRectF(-500,-500,1000,1000)
		self._rect_reticle = view_rect  or QtCore.QRectF(self._rect_scene)
		
		# Transforms
		self._scene_to_display_transform = QtGui.QTransform()
		"""Transform scene coordinate rects to viewport coordinate rects"""
		self._display_to_scene_transform = QtGui.QTransform()
		"""Transform display coordinates to scene coordinates (inverted from scene-to-display)"""

		# Mouse tracking
		self._mouse_thumbnail_offset   = QtCore.QPointF()
		"""The intitial offset of the mouse from the topLeft corner of the thumbnail rect, when it was clicked"""

		self._mouse_reticle_offset     = QtCore.QPointF()
		"""The initial offset of the mouse from the topLeft corner of the user reticle, when it was clicked"""
	
	def paintOverlay(self, painter, rect_canvas):
		
		super().paintOverlay(painter, rect_canvas)
		
		self._draw_thumbnail_base(painter)
		painter.drawPath(self._thumbnails_path.translated(self._thumb_display_offset))
		self._draw_user_reticle(painter)
		

		#painter.drawPolygon(self._thumbnails.)

	@QtCore.Slot(QtGui.QRegion)
	def setThumbnailRects(self, thumb_rects:list[QtCore.QRectF]):

		#print("Got", thumb_region)

		self.update(self.finalThumbnailRect())

		self._thumbnails_rects = thumb_rects

		self.buildThumbnailsPath()
		
		self.update(self.finalThumbnailRect())

	def buildThumbnailsPath(self):

		self.update(self.finalThumbnailRect())

		self._thumbnails_path = QtGui.QPainterPath()
		for thumb in self._thumbnails_rects:
			self._thumbnails_path.addRect(thumb)
		self._thumbnails_path = self._scene_to_display_transform.map(self._thumbnails_path)

		self.update(self.finalThumbnailRect())

	# Drawing

	def _draw_thumbnail_base(self, painter:QtGui.QPainter):

		pen_thumbnail = QtGui.QPen()
		pen_thumbnail.setColor(self.widget().palette().windowText().color())
		pen_thumbnail.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		pen_thumbnail.setWidthF(1)

		brush_thumbnail = QtGui.QBrush()
		brush_thumbnail.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		col_thumbnail = self.widget().palette().window().color()
		col_thumbnail.setAlphaF(0.75)
		brush_thumbnail.setColor(col_thumbnail)
		
		painter.setPen(pen_thumbnail)
		painter.setBrush(brush_thumbnail)
		painter.drawRect(self.finalThumbnailRect())


	def _draw_user_reticle(self, painter:QtGui.QPainter):

		if self._dragReticleActive():
			painter.setPen(self.widget().palette().accent().color().lighter())
		elif self.finalReticleRect().contains(self.widget().mapFromGlobal(QtGui.QCursor.pos())):
			painter.setPen(self.widget().palette().accent().color())
		painter.drawRect(self.finalReticleRect())

	# Calculations	

	def normalizedThumbnailRect(self) -> QtCore.QRectF:
		"""Thumbnail rect normalized to `topLeft=(0,0)`, `size=displaySize`"""

		return self._scene_to_display_transform.mapRect(self._rect_scene)
	
	def normalizedReticleRect(self) -> QtCore.QRectF:
		return self._scene_to_display_transform.mapRect(self._rect_reticle)
	
	def finalThumbnailRect(self) -> QtCore.QRectF:
		
		return self.normalizedThumbnailRect().translated(self._thumb_display_offset)
	
	def finalReticleRect(self) -> QtCore.QRectF:

		return self.normalizedReticleRect().translated(self._thumb_display_offset)
	
	# Properties

	@QtCore.Slot(QtCore.QRectF)
	def setSceneRect(self, scene_rect:QtCore.QRectF):

		if self._rect_scene == scene_rect:
			return
		
		if not scene_rect.isValid():
			return
		
		old_rect = self.normalizedThumbnailRect()
		self.update(old_rect)

		self._rect_scene = scene_rect

		# Update transform:
		# Get scene rect to display coords: 0,0 - scaled width,height using transform
		transform = QtGui.QTransform()
		transform.scale(self._thumb_display_size.width()/scene_rect.width(), self._thumb_display_size.width()/scene_rect.width())
		transform.translate(-scene_rect.left(), -scene_rect.top())
		
		self._scene_to_display_transform   = transform
		self._display_to_scene_transform, was_it_tho = transform.inverted()

		if not was_it_tho:
			raise ValueError("Unable to invert display-to-scene transform")

		self.sig_scene_rect_changed.emit(scene_rect)

		new_rect = self.normalizedThumbnailRect()
		self.setSceneRect(self.sceneRect())
		self.update(new_rect)
	
	def sceneRect(self) -> QtCore.QRectF:
		return self._rect_scene
	
	@QtCore.Slot(QtCore.QSizeF)
	def setThumbnailSize(self, thumbnail_size:QtCore.QSizeF):
		
		if self._thumb_display_size == thumbnail_size:
			return
		
		old_rect = self.normalizedThumbnailRect()
		self.update(old_rect)

		self._thumb_display_size = thumbnail_size
		self.sig_thumbnail_size_changed.emit(thumbnail_size)

		new_rect = self.normalizedThumbnailRect()
		self.update(new_rect)
	
	def thumbnailSize(self) -> QtCore.QSizeF:
		return self._thumb_display_size
	
	@QtCore.Slot(QtCore.QPointF)
	def setThumbnailOffset(self, offset:QtCore.QPointF):

		if self._thumb_display_offset == offset:
			return False
		
		old_rect = self.finalThumbnailRect()
		self.update(old_rect)
		
		# Check bounds
		canvas = QtCore.QRectF(self.widget().rect()).marginsRemoved(self._thumb_display_margins)
		if not canvas.contains(offset):
			# TODO: Based on orientation, set max to also query the opposite side
			offset = QtCore.QPointF(max(canvas.left(), offset.x()), max(canvas.top(), offset.y()))

		self._thumb_display_offset = offset

		new_rect = self.finalThumbnailRect()
		self.update(new_rect)
	
	@QtCore.Slot(QtCore.QRectF)
	def setViewReticle(self, view_rect:QtCore.QRectF):

		if self._rect_reticle == view_rect:
			return
		
		old_rect = self.normalizedThumbnailRect()
		self.update(old_rect)

		self._rect_reticle = view_rect
		self.sig_view_reticle_changed.emit(view_rect)

		new_rect = self.normalizedThumbnailRect()
		self.update(new_rect)

	def viewReticle(self) -> QtCore.QRectF:
		return self._rect_reticle
	
	# Events

	def event(self, event):
		
		if event.type() == QtCore.QEvent.Type.MouseButtonPress:
			return self._handleMouseButtonPress(event)
		
		if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
			return self._handleMouseDoubleClick(event)
		
		elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
			return self._handleMouseButtonRelease(event)
		
		elif event.type() == QtCore.QEvent.Type.MouseMove:
			return self._handleMouseMove(event)
		
		return super().event(event)
	
	def _dragThumbnailActive(self) -> bool:
		"""Is user dragging thumbnail?"""
		
		return not self._mouse_thumbnail_offset.isNull()
	
	def _dragReticleActive(self) -> bool:
		"""Is user dragging reticle?"""

		return not self._mouse_reticle_offset.isNull()
	
	def _handleMouseDoubleClick(self, event:QtGui.QMouseEvent) -> bool:
		"""Ignore double-clicks"""

		return self.finalReticleRect().contains(event.position())
	
	def _handleMouseDragReticle(self, event:QtGui.QMouseEvent) -> bool:
		"""Mouse reticle was clicked/dragged"""

		scene_pos = self._display_to_scene_transform.map(self._mouse_reticle_offset)
		self.sig_view_reticle_panned.emit(scene_pos)

		return True
	
	def _handleMouseButtonPress(self, event:QtGui.QMouseEvent) -> bool:

		if any((
			self._dragThumbnailActive(),
			self._dragReticleActive(),
			not self.finalThumbnailRect().contains(event.position())
		)):
			# Ignore weird mouse presses during active drags or outside of bounds
			return False
		
		if event.modifiers() & DEFAULT_KEY_DRAG_THUMBNAIL:
			# Begin alternative drag (move thumbnail)
			
			self.widget().setCursor(QtCore.Qt.CursorShape.DragMoveCursor)
			self._mouse_thumbnail_offset = event.position() - self.finalThumbnailRect().topLeft()
			
			return True

		else:
			# Begin normal click-to-center/drag of the reticle
			
			self._mouse_reticle_offset = event.position() - self.finalThumbnailRect().topLeft()
			self.update(self.finalReticleRect())
			return self._handleMouseDragReticle(event)

	def _handleMouseButtonRelease(self, event:QtGui.QMouseEvent):

		if self._dragThumbnailActive():
			# End alternative drag
			
			self.widget().unsetCursor()
			self._mouse_thumbnail_offset = QtCore.QPointF()
			
			return True
		
		if self._dragReticleActive():
			# End reticle drag

			self._mouse_reticle_offset = QtCore.QPointF()
			self.update(self.finalReticleRect())
			return True
	
		return False
		
	def _handleMouseMove(self, event:QtGui.QMouseEvent):
		
		if self._dragThumbnailActive():
			# Handle thumbnail drag
			
			self.setThumbnailOffset(event.position() - self._mouse_thumbnail_offset)
			return True
		
		elif self._dragReticleActive():
			# Handle click/drag reticle
			
			self._mouse_reticle_offset = event.position() - self.finalThumbnailRect().topLeft()
			self._handleMouseDragReticle(event)
			return True
		
		elif self.finalReticleRect().contains(event.position()):
			# Just repaint on hover for effects
			
			self.update(self.finalThumbnailRect())
			return False

		return False