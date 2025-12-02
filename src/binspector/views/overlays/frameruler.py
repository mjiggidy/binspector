import logging
from PySide6 import QtCore, QtGui

class BSAbstractFrameOverlay(QtCore.QObject):

	def paintOverlay(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRect, rect_dirty:QtCore.QRect):
		"""Paint the overlay, with the given paintEvent"""
		
class BSGraphicsOverlayManager(QtCore.QObject):

	sig_overlay_installed  = QtCore.Signal(object)
	sig_overlay_removed    = QtCore.Signal(object)

	def __init__(self, *args, parent, **kwargs):

		super().__init__(*args, parent=parent, **kwargs)

		self._overlays:set[BSAbstractFrameOverlay] = set()
	
	def overlays(self) -> list[BSAbstractFrameOverlay]:
		"""Get all installed overlays"""

		return list(self._overlays)
	
	def installOverlay(self, overlay:BSAbstractFrameOverlay):
		"""Install a new overlay"""

		if overlay not in self._overlays:

			overlay.setParent(self)
			self._overlays.add(overlay)

			logging.getLogger(__name__).debug("Added overlay %s", overlay)
			self.sig_overlay_installed.emit(overlay)

	def removeOverlay(self, overlay:BSAbstractFrameOverlay):
		"""Remove an installed overlay"""

		try:
			self._overlays.remove(overlay)
		except KeyError as e:
			raise ValueError(f"Overlay {overlay} not installed in this manager") from e
		
		logging.getLogger(__name__).debug("Removed overlay %s", overlay)
		
		self.sig_overlay_removed(overlay)
		overlay.deleteLater()

	def paintOverlays(self, painter:QtGui.QPainter, rect:QtCore.QRect):
		"""Paint installed overlays"""

		for overlay in self._overlays:

			try:
				overlay.paintOverlay(painter, rect)

			except Exception as e:
				logging.getLogger(__name__).error("Error painting %s: %s", overlay, e)
		
class BSFrameRulerOverlay(BSAbstractFrameOverlay):

	sig_enabled_toggled = QtCore.Signal(bool)

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._is_enabled = True

		try:
			self._viewport = self.parent().viewport()
		except ValueError as e:
			raise ValueError("Parent must have a viewport") from e

		# Pens
		self._pen_ruler_edge    = QtGui.QPen()
		self._pen_ruler_base    = QtGui.QPen()
		self._pen_mouse_coords  = QtGui.QPen()

		# Brushes

		# Fonts
		self._font_mouse_coords = QtGui.QFont()

		print("HELLO FROM ME")

	def isEnabled(self) -> bool:

		return self._is_enabled
	
	@QtCore.Slot(bool)
	def setIsEnabled(self, is_enabled:bool):

		if not self._is_enabled == is_enabled:

			self._is_enabled = is_enabled
			self.sig_enabled_toggled.emit(self._is_enabled)
	
	@QtCore.Slot()
	def toggle(self):

		self.setIsEnabled(not self._is_enabled)

	def  paintOverlay(self, painter, rect_canvas, rect_dirty):

		painter.save()
		print("Hello from ", self)
		painter.restore()

		return super().paintOverlay(painter, rect_canvas, rect_dirty)