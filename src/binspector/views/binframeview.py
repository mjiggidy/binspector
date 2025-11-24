import logging
from PySide6 import QtCore, QtGui, QtWidgets


class BSPinchEventHandler(QtCore.QObject):
	"""I peench"""

	sig_user_is_pinching    = QtCore.Signal(float)
	"""User did a pinchy"""

	sig_user_finished_pinch = QtCore.Signal(QtWidgets.QPinchGesture)
	"""User tired of the pinch"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		logging.getLogger(__name__).error("Hello from me")
	
	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):

		if event.type() == QtCore.QEvent.Type.NativeGesture and \
		  event.gestureType() == QtCore.Qt.NativeGestureType.ZoomNativeGesture:
		
			self.reportPinchZoom(event)


		return super().eventFilter(watched, event)
	
	def reportPinchZoom(self, event:QtGui.QNativeGestureEvent):

		self.sig_user_is_pinching.emit(event.value())

	
	#def reportPinch(self, pinch_gesture:QtWidgets.QPinchGesture):
		
		#if pinch_gesture.state() in (QtCore.Qt.GestureState.GestureUpdated, QtCore.Qt.GestureState.GestureFinished):
	#	self.sig_user_is_pinching.emit(pinch_gesture)
		
	#	if pinch_gesture.state() == QtCore.Qt.GestureState.GestureFinished:
	#		self.sig_user_finished_pinch.emit(pinch_gesture)
	
	def reportPan(self, pan_gesture:QtWidgets.QPanGesture):

		print("Pan delta:", pan_gesture.delta())

class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	sig_zoom_level_changed = QtCore.Signal(int)
	sig_zoom_range_changed = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

		self._current_zoom = 1
		self._zoom_range   = range(100)

		# This is fancy for me. Heehee.
		# https://doc.qt.io/qtforpython-6/overviews/qtwidgets-gestures-overview.html
		#self.grabGesture(QtCore.Qt.GestureType.PinchGesture)
		#self.grabGesture(QtCore.Qt.GestureType.PanGesture)
		
		# TODO: Seems I need to grabGesture() before installing the event filter
		# or the event filter doesn't work? I don't know lol look at this later 
		# just to understand it better.  But I'm just saying: keep this order
		self._pinchy_boy   = BSPinchEventHandler(parent=self)
		self.installEventFilter(self._pinchy_boy)

		self._pinchy_boy.sig_user_is_pinching   .connect(self.reframeOnPinch, QtCore.Qt.ConnectionType.QueuedConnection)
		self._pinchy_boy.sig_user_finished_pinch.connect(self.userFinishedPinch)

	@QtCore.Slot(float)
	def reframeOnPinch(self, zoom_delta:float):
		
		#rect = self.sceneRect()
		#rect.translate(pinch_gesture.centerPoint())

		#print(pinch_gesture.centerPoint())
		#self.setSceneRect(rect)
		#print(pinch_gesture.scaleFactor())

		new_zoom = self._current_zoom + (zoom_delta)

		print(f"{zoom_delta=}")

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

	@QtCore.Slot(QtWidgets.QPinchGesture)
	def userFinishedPinch(self, pinch_gesture:QtWidgets.QPinchGesture):


		self.setZoom(max(self._zoom_range.start, min(round(self._current_zoom), self._zoom_range.stop)))

	@QtCore.Slot(object)
	def setZoomRange(self, zoom_range:range):

		if self._zoom_range != zoom_range:
			self._zoom_range = zoom_range
			self.sig_zoom_range_changed.emit(zoom_range)
	
	def zoomRange(self) -> range:
		return self._zoom_range

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setZoom(self, zoom_level:int|float):
		#print("I SET ZOOM", zoom_level)

		if zoom_level != self._current_zoom:
			
			
			#logging.getLogger(__name__).debug("Setting zoom level to %s", zoom_level)

			zoom_level = float(zoom_level) #/ float(4)
			self._current_zoom = zoom_level

			t = QtGui.QTransform()
			t.scale(zoom_level, zoom_level)
			self.setTransform(t)

			self.sig_zoom_level_changed.emit(zoom_level)
	
	def drawBackground(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		GRID_DIVISIONS = 3
		GRID_UNIT_SIZE = QtCore.QSizeF(18,12)

		pen_boundary = QtGui.QPen()
		pen_boundary.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen_boundary.setCosmetic(True)
		pen_boundary.setWidth(1)
		pen_boundary.setColor(self.parentWidget().palette().shadow().color())

		pen_division = QtGui.QPen()
		pen_division.setStyle(QtCore.Qt.PenStyle.DashLine)
		pen_division.setCosmetic(True)
		pen_division.setWidth(1)
		pen_division.setColor(self.parentWidget().palette().shadow().color())

		super().drawBackground(painter, rect)

		painter.save()

		# Setup stuff for ruler
		
		coord_font = self.font()
		coord_font.setPointSizeF(coord_font.pointSizeF()/(self._current_zoom))
		painter.setFont(coord_font)
		
		#import logging
		#logging.getLogger(__name__).debug("Set font size to %s px", coord_font.pointSizeF())

		mapped_viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()

		y_top = mapped_viewport_rect.top()
		x_left = mapped_viewport_rect.left()

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

			painter.drawText(QtCore.QPointF(x, float(y_top) - (float(y_top) - float(y_top + GRID_UNIT_SIZE.height()))-11), str(int(x)))
		
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

			painter.drawText(QtCore.QPoint(float(x_left) - (float(x_left) - float(x_left + GRID_UNIT_SIZE.width())+18), y), str(int(y)))

		painter.restore()