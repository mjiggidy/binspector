"""
An overlay widget for drawing above a widget and its children
"""

from PySide6 import QtCore, QtGui, QtWidgets

class BSAbstractOverlayWidget(QtWidgets.QWidget):
	"""A transparent widget for drawing above a given widget.  Note: Installs itself as an `eventFilter`."""

	def __init__(self, parent:QtWidgets.QWidget):

		super().__init__(parent=parent)

		self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
		self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)

		self.parent().installEventFilter(self)

	def eventFilter(self, watched:QtWidgets.QWidget, event:QtCore.QEvent):
		
		if event.type() == QtCore.QEvent.Type.Resize:
			self.resize(event.size())
			return True
		
		return super().eventFilter(watched, event)
	
class BSDragDropOverlayWidget(BSAbstractOverlayWidget):

	sig_margins_changed = QtCore.Signal(QtCore.QMarginsF)
	sig_enabled_changed = QtCore.Signal(bool)

	def __init__(self, parent:QtWidgets.QWidget, *args, margins:QtCore.QMarginsF|None=None, is_visible:bool=True, **kwargs):

		super().__init__(parent=parent)

		self._margins = margins or QtCore.QMarginsF(32,32,32,32)

		self.setVisible(is_visible)
	
	def margins(self) -> QtCore.QMarginsF:

		return self._margins
	
	@QtCore.Slot(QtCore.QMarginsF)
	def setMargins(self, margins:QtCore.QMarginsF):

		if self._margins == margins:
			return
		
		self._margins = QtCore.QMarginsF(margins)

		if self.isVisible():
			self.update()

		self.sig_margins_changed.emit(margins)

	def paintEvent(self, event:QtGui.QPaintEvent):

		if not self.isVisible():
			print("NOPE")
			return

		pen = QtGui.QPen()
		pen.setWidth(10)
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setColor(self.parent().palette().highlight().color())

		painter = QtGui.QPainter(self)
		painter.setPen(pen)
		painter.drawRoundedRect(
			QtCore.QRectF(self.parent().rect()).marginsRemoved(self._margins), 10, 10, QtCore.Qt.SizeMode.AbsoluteSize)
		painter.end()