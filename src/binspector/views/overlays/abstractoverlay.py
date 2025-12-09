
from PySide6 import QtCore, QtGui, QtWidgets

class BSAbstractOverlay(QtCore.QObject):
	"""Abstract overlay for display over a widget"""
	
	sig_enabled_changed       = QtCore.Signal(bool)
	sig_update_rect_requested = QtCore.Signal(object)
	sig_update_requested      = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._is_enabled:bool = True
		self._font    = QtWidgets.QApplication.font()
		self._palette = QtWidgets.QApplication.palette()
		self._widget  = QtWidgets.QWidget()
	
	def update(self, update_rect:QtCore.QRectF|None=None):
		
		if update_rect:
			self.sig_update_rect_requested.emit(update_rect)
		else:
			self.sig_update_requested.emit()
	
	def paintOverlay(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRect):
		"""Paint the overlay, with the given paintEvent"""
		# Virtual method

	def widget(self) -> QtWidgets.QWidget:
		"""The widget this overlay draws to"""

		return self._widget
	
	def _setWidget(self, widget:QtWidgets.QWidget):
	
		self._widget = widget

#   NOTE: Not doin' me no palette for no now
#	@QtCore.Slot(QtGui.QPalette)
#	def setPalette(self, new_palette:QtGui.QPalette):
#
#		if self._palette != new_palette:
#			self._palette = new_palette
#			self.sig_update_requested.emit()

	def palette(self) -> QtGui.QPalette:

		return self.widget().palette()
	
	@QtCore.Slot(QtGui.QFont)
	def setFont(self, new_font:QtGui.QFont):

		if self._font != new_font:
			self._font = new_font
			self.sig_update_requested.emit()
	
	def isEnabled(self) -> bool:
		"""Overlay is enabled"""

		return self._is_enabled
	
	@QtCore.Slot(bool)
	def _setEnabled(self, is_enabled:bool):
		"""This should be set via the manager"""

		if not self._is_enabled == is_enabled:

			self._is_enabled = is_enabled
			self.sig_enabled_changed.emit(is_enabled)
			self.sig_update_requested.emit()