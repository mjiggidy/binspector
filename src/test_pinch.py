import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.managers import eventfilters

class MichaelsCoolVisualizerOfThePinch(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._curve_scale = QtCore.QEasingCurve()
		self._curve_scale.setType(QtCore.QEasingCurve.Type.InOutQuad)

		self._brush = QtGui.QBrush(self.palette().dark())
		self._brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		self._pen = QtGui.QPen(self.palette().windowText().color())
		self._pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
		self._pen.setWidth(3)

		self._scale_delta = 1
		self._scale_scale = 1

		self._animator = QtCore.QPropertyAnimation()
		self._animator.setParent(self)
		self._animator.setTargetObject(self)
		self._animator.setPropertyName(QtCore.QByteArray.fromStdString("scale"))
		self._animator.setDuration(500) # Msec
		self._animator.setEasingCurve(QtCore.QEasingCurve.Type.OutElastic)
		

	@QtCore.Property(float)
	def scale(self) -> float:

		return self._scale_delta

	@scale.setter
	def scale(self, scale:float):

		self._scale_delta = scale
		self.update()
	
	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(100,100)
	
	@QtCore.Slot(object)
	def setScaleDelta(self, delta:float|None=None):
		
		delta = delta or 0
		self.scale = 1 + (delta * self._scale_scale)

		self.update()
	
	def resetScale(self):

		self._animator.setStartValue(self._scale_delta)
		self._animator.setEndValue(1)
		self._animator.start()


	def paintEvent(self, event:QtGui.QPaintEvent):
		
		# Ironically NOT using an event filter here lol
		
		super().paintEvent(event)

		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

		try:
			self.drawVisualizer(painter, event.rect())
		except Exception as e:
			print(e, file=sys.stderr)
		finally:
			painter.end()

	def drawVisualizer(self, painter:QtGui.QPainter, bounding_rect:QtCore.QRect):
		
		painter.save()

		painter.setPen(self._pen)
		painter.setBrush(self._brush)
		painter.drawEllipse(
			bounding_rect.center(),
			(bounding_rect.width()/2  - painter.pen().width()*2) * self._scale_delta,
			(bounding_rect.height()/2 - painter.pen().width()*2) * self._scale_delta
		)

		painter.drawText(
			bounding_rect,
			QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter,
			str(round(self._scale_delta, 1))
		)

		painter.restore()

class MichaelsCoolTestWindowHahaOk(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._pinch_event_filter = eventfilters.BSPinchEventFilter(parent=self)
		self._visualizer = MichaelsCoolVisualizerOfThePinch()

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().addWidget(self._visualizer)

		self.installEventFilter(self._pinch_event_filter)
		
		self._pinch_event_filter.sig_user_is_pinching.connect(self._visualizer.setScaleDelta)
		self._pinch_event_filter.sig_user_finished_gesture.connect(self._visualizer.resetScale)

if __name__ == "__main__":

	import logging
	#logging.basicConfig(level=logging.DEBUG)

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = MichaelsCoolTestWindowHahaOk()
	wnd.show()

	sys.exit(app.exec())