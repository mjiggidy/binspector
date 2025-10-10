from ..widgets import mainwindow
from PySide6 import QtCore, QtWidgets

class BSWindowManager(QtCore.QObject):
	"""Main window manager (for scoping etc)"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._windows:list[QtWidgets.QWidget] = list()
	
	def createMainWindow(self) -> mainwindow.BSMainWindow:

		window = mainwindow.BSMainWindow()
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self._addWindow(window)
		
		return window
	
	def _addWindow(self, window:QtWidgets.QWidget):
		"""Add an existing window"""

		if window in self._windows:
			return
		
		self._windows.append(window)
		window.destroyed.connect(lambda w: self._removeWindow(w))
	
	@QtCore.Slot(object)
	def _removeWindow(self, window:QtWidgets.QWidget):

		# NOTE: This is not good yet.

		try:
			self._windows.remove(window)
		except ValueError:
			pass
