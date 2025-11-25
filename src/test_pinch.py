import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.managers import eventfilters

class MichaelsCoolVisualizerOfThePinch(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._curve_scale = QtCore.QEasingCurve()

		self._brush = QtGui.QBrush()
		self._pen   = QtGui.QPen()
		self._font  = self.font()

		self._scale_sensitivity = 0.5
		self._resting_scale     = 0.8
		self._current_scale     = self._resting_scale

		self._curve_scale.setType(QtCore.QEasingCurve.Type.InOutQuad)
		
		self._animator = QtCore.QPropertyAnimation()
		self._animator.setParent(self)
		self._animator.setTargetObject(self)
		self._animator.setPropertyName(QtCore.QByteArray.fromStdString("scale"))
		self._animator.setDuration(500) # Msec
		self._animator.setEasingCurve(QtCore.QEasingCurve.Type.OutElastic)

		self._setupPainters()

	def event(self, event:QtCore.QEvent) -> bool:

		if not event.type() == QtCore.QEvent.Type.PaletteChange:
			return super().event(event)
		
		self._setupPainters()
		return True

	def _setupPainters(self):

		self._brush = self.style().standardPalette().midlight()
		self._brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		self._pen.setColor(self.style().standardPalette().windowText().color())
		self._pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
		self._pen.setWidth(3)

		self._font = self.font()
		self._font.setPointSizeF(self.font().pointSizeF() * 0.8)

	@QtCore.Property(float)
	def scale(self) -> float:
		"""Needed for QPropertyAnimation"""

		return self._current_scale

	@scale.setter
	def scale(self, scale:float):
		"""Needed for QPropertyAnimation"""

		self._current_scale = scale
		self.update()
	
	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(100,100)
	
	@QtCore.Slot(float)
	def setScaleDelta(self, accumulated:float|None=None):
		"""Process delta and use it"""
		
		accumulated = accumulated or 0
		self.scale = max(0.1, min(self._resting_scale + (accumulated * self._scale_sensitivity), 2))

		self.update()
	
	def resetScale(self):

		self._animator.stop()
		self._animator.setStartValue(self._current_scale)
		self._animator.setEndValue(self._resting_scale)
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
		
		base_rad = min(bounding_rect.width(), bounding_rect.height()) / 2 - painter.pen().widthF() * 2

		painter.save()

		painter.setPen(self._pen)
		painter.setBrush(self._brush)
		painter.setFont(self._font)
		painter.drawEllipse(
			bounding_rect.center(),
			base_rad * self._current_scale,
			base_rad * self._current_scale
		)

		painter.drawText(
			bounding_rect,
			QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter,
			str(round(self._current_scale, 2))
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
		
		self._pinch_event_filter.sig_user_started_gesture.connect(self._visualizer._animator.stop)
		self._pinch_event_filter.sig_user_is_pinching.connect(lambda d,a: self._visualizer.setScaleDelta(a))
		self._pinch_event_filter.sig_user_finished_gesture.connect(self._visualizer.resetScale)

if __name__ == "__main__":

	import logging
	logging.basicConfig(level=logging.DEBUG)

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = MichaelsCoolTestWindowHahaOk()
	wnd.show()

	sys.exit(app.exec())