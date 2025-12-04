from PySide6 import QtCore, QtGui, QtWidgets
from ...managers import overlaymanager

class BSAbstractOverlay(QtCore.QObject):
	"""Abstract overlay for display over a widget"""
	
	sig_enabled_changed  = QtCore.Signal(bool)
	sig_update_requested = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		

		super().__init__(*args, **kwargs)

		self._is_enabled:bool = True
		self._font    = QtWidgets.QApplication.font()
		self._palette = QtWidgets.QApplication.palette()
	
	
	def paintOverlay(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRect, rect_dirty:QtCore.QRect|None=None):
		"""Paint the overlay, with the given paintEvent"""
		# Virtual method

	def eventOverlay(self, event:QtCore.QEvent) -> bool:
		"""Event handler for overlays"""
		# Virtual method
		return False

	def widget(self) -> QtWidgets.QWidget:
		"""The widget this overlay draws to"""

		return self.parent().parent()

	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, new_palette:QtGui.QPalette):

		if self._palette != new_palette:
			self._palette = new_palette
	
	@QtCore.Slot(QtGui.QFont)
	def setFont(self, new_font:QtGui.QFont):

		if self._font != new_font:
			self._font = new_font
	
	def isEnabled(self) -> bool:
		"""Overlay is enabled"""

		return self._is_enabled
	
	@QtCore.Slot(bool)
	def setIsEnabled(self, is_enabled:bool):

		if not self._is_enabled == is_enabled:

			self._is_enabled = is_enabled
			self.sig_enabled_changed.emit(self._is_enabled)
	
	@QtCore.Slot()
	def toggle(self):
		"""Toggle overlay enabled state"""

		self.setIsEnabled(not self._is_enabled)
	
