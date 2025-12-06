from PySide6 import QtCore, QtGui
from . import abstractoverlay

DEFAULT_DISPLAY_SIZE      = QtCore.QSizeF(200, 300)
DEFAULT_DISPLAY_MARGINS   = QtCore.QMarginsF(50, 40, 26, 36)
DEFAULT_DISPLAY_ALIGNMENT = QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignRight
DEFAULT_DISPLAY_POSITION  = QtCore.QPointF(0,0)

class BSFrameMapOverlay(abstractoverlay.BSAbstractOverlay):
	"""A thumbnail map overlay thing"""

	sig_display_alignment_changed = QtCore.Signal(QtCore.Qt.AlignmentFlag)
	sig_display_position_changed  = QtCore.Signal(QtCore.QPointF)
	sig_display_size_changed      = QtCore.Signal(QtCore.QSizeF)
	sig_scene_rect_changed        = QtCore.Signal(QtCore.QRectF)

	def __init__(self,
		*args,
		display_size:      QtCore.QSize|QtCore.QSizeF|None =None,
		display_alignment: QtCore.Qt.AlignmentFlag|None    =None,
		display_position:  QtCore.QPointF|None             =None,
		display_margin:    QtCore.QMarginsF|None           =None,
		scene_rect:        QtCore.QRect|QtCore.QRectF      =None,
		**kwargs):

		super().__init__(*args, **kwargs)

		self._display_size = display_size or DEFAULT_DISPLAY_SIZE
		self._display_margins = display_margin or DEFAULT_DISPLAY_MARGINS
		self._display_alignment = display_alignment or DEFAULT_DISPLAY_ALIGNMENT
		self._display_position = display_position or DEFAULT_DISPLAY_POSITION

		self._scene_rect = self._display_size

		self._mouse_drag_start   = QtCore.QPointF()
		
		self._scene_rect = scene_rect or QtCore.QRectF()

		
	
	def _dragIsActive(self) -> bool:
		"""User is currently dragging"""

		return not self._mouse_drag_start.isNull()
	
	def sceneRect(self) -> QtCore.QRectF:
		return self._scene_rect
	
	@QtCore.Slot(QtCore.QRectF)
	def setSceneRect(self, scene_rect:QtCore.QRectF):

		if self._scene_rect != scene_rect:

			old_rect = self.displayRect()
			self.update(old_rect)

			self._scene_rect = scene_rect
			self.sig_scene_rect_changed.emit(scene_rect)
			self.update(scene_rect)
	
	@QtCore.Slot(QtCore.QSizeF)
	def setDisplaySize(self, display_size:QtCore.QSizeF):

		if not self._display_size == display_size:
			
			old_rect = self.displayRect()
			self.update(old_rect)
			
			self._display_size = display_size
			self.sig_display_size_changed.emit(display_size)
			
			new_rect = self.displayRect()
			self.update(new_rect)
		
	def displaySize(self) -> QtCore.QSizeF:

		return self._display_size

	@QtCore.Slot(QtCore.Qt.AlignmentFlag)
	def setAlignment(self, alignment:QtCore.Qt.AlignmentFlag):

		if not self._display_alignment == alignment:

			old_rect = self.displayRect()
			self.update(old_rect)

			self._display_alignment = alignment
			self.sig_display_alignment_changed.emit(alignment)

			new_rect = self.displayRect()
			self.update(self.displayRect(new_rect))

	def alignment(self) -> QtCore.Qt.AlignmentFlag:

		return self._display_alignment
	
	@QtCore.Slot(QtCore.QPointF)
	def setDisplayPositionOffset(self, position_offset:QtCore.QPointF):

		if self._display_position != position_offset:

			old_rect = self.displayRect()
			self.update(old_rect)

			self._display_position += position_offset
			self.sig_display_position_changed.emit(position_offset)

			new_rect = self.displayRect()
			self.update(new_rect)

	def positionOffset(self) -> QtCore.QPointF:

		return self._display_position

	def paintOverlay(self, painter, rect_canvas):

		

		self._draw_frame(painter, rect_canvas)

		#return super().paintOverlay(painter, rect_canvas)

	def _draw_frame(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF|None=None):

		rect_frame = self.displayRect(rect_canvas)
		#print(rect_frame)

		brush = self._palette.window()
		pen   = QtGui.QPen(self._palette.windowText().color())
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		pen.setWidthF(3)

		painter.setBrush(brush)
		painter.setPen(pen)

		painter.drawRect(rect_frame)


	
	def displayRect(self, rect_canvas:QtCore.QRectF|None=None) -> QtCore.QRectF:
		"""The display rect relative to the canvas"""

		rect_canvas = rect_canvas or self.widget().rect()

		display_rect = QtCore.QRectF(
			QtCore.QPoint(0,0),
			self._scene_rect.size().scaled(
				self._display_size,
				QtCore.Qt.AspectRatioMode.KeepAspectRatio
			)
		).marginsAdded(self._display_margins)

		# Horizontal alignment
		if self._display_alignment & QtCore.Qt.AlignmentFlag.AlignLeft:
			display_rect.moveLeft(rect_canvas.left())
		elif self._display_alignment & QtCore.Qt.AlignmentFlag.AlignHCenter:
			display_rect.moveCenter(rect_canvas.center().x(), display_rect.y())
		else:
			display_rect.moveRight(rect_canvas.right())
	
		# Vertical alignment
		if self._display_alignment & QtCore.Qt.AlignmentFlag.AlignBottom:
			display_rect.moveBottom(rect_canvas.bottom())
		elif self._display_alignment& QtCore.Qt.AlignmentFlag.AlignVCenter:
			display_rect.moveCenter(display_rect.x(), rect_canvas.center().y())
		else:
			display_rect.moveTop(rect_canvas.top())
		
		display_rect.translate(self._display_position)
		return  display_rect.marginsRemoved(self._display_margins)
	

	def beginUserDragDisplayRect(self, drag_start_position:QtCore.QPointF) -> bool:
		
		# Start position relative to the top left corner of the display rect
		self._mouse_drag_start = drag_start_position - self.displayRect().topLeft()
		self.update(self.displayRect())

		return True
	
	def updateUserDragDisplayRect(self, drag_update_position:QtCore.QPointF) -> bool:

		if not self._dragIsActive():
			return False
		
		self.update(self.displayRect())

		drag_update_position -= self.displayRect().topLeft() + self._mouse_drag_start
		
		
		#print(drag_update_position)
		# self.setDisplayPositionOffset calls update()
		self.setDisplayPositionOffset(drag_update_position)

		return True
	
	def endUserDragDisplayRect(self) -> bool:

		self._mouse_drag_start = QtCore.QPointF()
		self.update(self.displayRect())
		return True
	
	def event(self, event):

		if event.type() == QtCore.QEvent.Type.MouseButtonPress:
			
			if not self.displayRect(self.widget().rect()).contains(event.position()):
				return False
			
			if event.buttons() & QtCore.Qt.MouseButton.LeftButton and event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
				return self.beginUserDragDisplayRect(event.position())
			
			return True
		
		elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._dragIsActive():
			return self.endUserDragDisplayRect()
		
		elif event.type() == QtCore.QEvent.Type.MouseMove:

			#self.setMouseCoordinates(event.position())
			if self._dragIsActive():
				return self.updateUserDragDisplayRect(event.position())

		elif event.type() == QtCore.QEvent.Type.Resize:
			self.update(self.widget().rect())

		return super().event(event)
	
