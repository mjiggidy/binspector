from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from PySide6 import QtCore, QtGui, QtWidgets
from ..views.overlays import abstractoverlay
		
class BSGraphicsOverlayManager(QtCore.QObject):
	"""Overlay manager for a widget"""

	sig_overlay_installed  = QtCore.Signal(object)
	sig_overlay_removed    = QtCore.Signal(object)

	def __init__(self, *args, parent:QtWidgets.QWidget, **kwargs):

		if not isinstance(parent, QtWidgets.QWidget):
			raise ValueError(f"Parent must be a `QWidget` (got {type(parent)})")

		super().__init__(*args, parent=parent, **kwargs)

		self._overlays:set[abstractoverlay.BSAbstractOverlay] = set()

		self._installOnParent()

	def _installOnParent(self):
		"""Hook manager into the parent widget event loop"""

		self.parent().installEventFilter(self)

	
	def overlays(self) -> list[abstractoverlay.BSAbstractOverlay]:
		"""Get all installed overlays"""

		return list(self._overlays)
	
	def installOverlay(self, overlay:abstractoverlay.BSAbstractOverlay):
		"""Install a new overlay"""

		if overlay not in self._overlays:

			self._overlays.add(overlay)
			self.installEventFilter(overlay)
			
			overlay.setParent(self)
			overlay._setWidget(self.parent())
			overlay.setPalette(self.parent().palette())
			
			overlay.sig_update_requested.connect(self.parent().update)
			overlay.sig_update_rect_requested.connect(self.parent().update)
			
			logging.getLogger(__name__).debug("Installed parent %s on %s", overlay.parent(), overlay)
			self.sig_overlay_installed.emit(overlay)

	def removeOverlay(self, overlay:abstractoverlay.BSAbstractOverlay):
		"""Remove an installed overlay"""

		try:
			self._overlays.remove(overlay)
		except KeyError as e:
			raise ValueError(f"Overlay {overlay} not installed in this manager") from e
		
		logging.getLogger(__name__).debug("Removed overlay %s", overlay)
		
		overlay.disconnect(self)
		self.disconnect(overlay)
		self.sig_overlay_removed.emit(overlay)
		overlay.deleteLater()

	# NOTE: May be able to take care of these via events?
	@QtCore.Slot(QtGui.QFont)
	def setFont(self, new_font:QtGui.QFont):

		for overlay in self._overlays:
			overlay.setFont(new_font)
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, new_palette:QtGui.QPalette):
		
		for overlay in self._overlays:
			overlay.setPalette(new_palette)

	def paintOverlays(self, painter:QtGui.QPainter, rect:QtCore.QRect):
		"""Paint installed overlays"""

		for overlay in self._overlays:

			painter.save()
			
			if not overlay.isEnabled():
				continue
			try:
				overlay.paintOverlay(painter, rect)
			except Exception as e:
				logging.getLogger(__name__).error("Error painting %s: %s", overlay, e)
			finally:
				painter.restore()
	
	def eventFilter(self, watched:QtWidgets.QWidget, event:QtCore.QEvent):
		"""Foreward events to active overlays"""

		# Ignore paint events -- must be handled via parent widget's paintEvent
		if event.type() == QtCore.QEvent.Type.Paint:
			return False
		
		for overlay in filter(lambda o: o.isEnabled(), self._overlays):

			if QtWidgets.QApplication.sendEvent(overlay, event):
				return True
		
		return False