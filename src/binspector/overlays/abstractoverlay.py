from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
	from ..managers import overlaymanager

class BSAbstractOverlay(QtCore.QObject):
	"""Abstract overlay for display over a widget"""
	
	sig_enabled_changed       = QtCore.Signal(bool)
	sig_update_rect_requested = QtCore.Signal(object)
	sig_update_requested      = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._is_enabled:bool = True
	
	def update(self, update_rect:QtCore.QRectF|None=None):
		
		if update_rect:
			self.sig_update_rect_requested.emit(update_rect)
		else:
			self.sig_update_requested.emit()
	
	def paintOverlay(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRect):
		"""Paint the overlay, with the given paintEvent"""
		# Virtual method

	def _widgetInfo(self) -> overlaymanager.BSOverlayParentWidgetInfo|None:
		"""Overlay's parent widget info"""
		
		# NOTE TO SELF: Preferring not to acces this directly from overlays
		# as this returns references to the Qt data objects instead of copies.
		# Use palette(), font(), rect() etc instead
		return self.parent().widgetInfo() if self.parent() else None

	def palette(self) -> QtGui.QPalette:
		"""Overlay's parent widget palette"""

		return QtGui.QPalette(self.parent().widgetInfo().palette) if self.parent() \
			else QtWidgets.QApplication.palette()
	
	def font(self) -> QtGui.QFont:
		"""Overlay's parent widget font"""

		return QtGui.QFont(self.parent().widgetInfo().font) if self.parent() \
			else QtWidgets.QApplication.font()
	
	def rect(self) -> QtCore.QRect:
		"""Overlay's parent widget rect"""

		return QtCore.QRectF(self.parent().widgetInfo().rect) if self.parent() \
			else QtCore.QRectF(QtCore.QPointF(0,0), QtCore.QSizeF(100,100))
	
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