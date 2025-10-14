"""
Window managers
"""

from PySide6 import QtCore, QtGui, QtWidgets
from ..widgets import mainwindow

class BSWindowManager(QtCore.QObject):
	"""Main window manager (for scoping etc)"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._windows:list[QtWidgets.QWidget] = list()
	
	def addWindow(self, window:QtWidgets.QWidget) -> QtWidgets.QWidget:
		"""Add an existing window (and returns it again, unchanged)"""
		
		if window in self._windows:
			return window
		
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		window.destroyed.connect(self._removeWindow)

		self._windows.append(window)
		
		return window
	
	@QtCore.Slot(object)
	def _removeWindow(self, window:QtWidgets.QWidget):

		# NOTE: This is a total mess

		try:
			self._windows.remove(window)
			print("Removed")
		except Exception as e:
			print(e, len(self._windows))

# Create new window: 
# - From an active window? Offset diagonally from current with same size
# - First window? Create at last known window geo
# - Otherwise center of primary screen

# Window activated OR moved/resized
# - Fire off timer to save geo of last active window

class BSWindowSettingsManager(QtCore.QObject):
	"""Save last window geometry"""

	# TODO: Lots of redundant slots here, clean up
	# Basically:
	# - Watches screens for changes to layout or resolution
	# - 

	def __init__(self,
		window:QtWidgets.QWidget,
		settings:QtCore.QSettings,
		settings_name:str,
		relative_to:QtWidgets.QWidget|None=None	# Position relative to another window? Not used.
	):

		super().__init__()
		
		self._window = window
		self._settings = settings
		self._settings_name = settings_name
		self._wndow_relative_to = relative_to

		self._timer_window_geometry = QtCore.QTimer(singleShot=True, interval=200)

		self._setupSignals()

		self._window.installEventFilter(self)

	def _setupSignals(self):

		# Timer to save window geometry changes (fired via self.eventFilter)
		self._timer_window_geometry.timeout.connect(self.saveWindowGeometry)

		# Screens added or removed
		QtWidgets.QApplication.instance().screenAdded.connect(self.screenWasAdded)
		QtWidgets.QApplication.instance().screenAdded.connect(self.screenLayoutChanged)
		QtWidgets.QApplication.instance().screenRemoved.connect(self.screenLayoutChanged)

	def window(self) -> QtWidgets.QWidget:
		"""Get the window this is managing"""

		return self._window

	@QtCore.Slot(QtGui.QScreen)
	def screenWasAdded(self, screen:QtGui.QScreen):
		"""Setup listeners for screens added/removed/changed"""

		# TODO: screenWasAdded & screenLayoutChanged currently
		# just pass through to restoreWindowGeometry. So probably
		# get rid of these

		screen.geometryChanged.connect(self.screenLayoutChanged)

	@QtCore.Slot(QtGui.QScreen)	# screenAdded/screenRemoved
	@QtCore.Slot(QtCore.QRect)	# geometryChanged
	def screenLayoutChanged(self, changed:QtGui.QScreen|QtCore.QRect):
		"""Screens were added, removed, or changed"""

		self.restoreWindowGeometry()

	@QtCore.Slot()
	def restoreWindowGeometry(self):
		"""Restore a window's position from settings (or default)"""

		# NOTE: Screen geometry and window geometry are both returned as `QRect`s
		# in a global space.  So, will want to validate QScreen.geometry().contains(QWindow.geometry())

		saved_window_geometry = self._settings.value(self._settings_name+"/window_geometry", self._window.geometry())

		new_window_geometry = None

		for screen in QtWidgets.QApplication.screens():
			if screen.geometry().contains(saved_window_geometry):
				new_window_geometry = saved_window_geometry
		
		# Center window in primary screen if nothing else
		# NOTE: Maybe adapt this for "relative to" windows
		if new_window_geometry is None:
			primary_screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
			new_window_geometry = saved_window_geometry
			new_window_geometry.moveCenter(primary_screen_geometry.center())

		self._window.setGeometry(new_window_geometry)
	
	@QtCore.Slot()
	def saveWindowGeometry(self):
		"""Save a window's geometry"""

		self._settings.setValue(self._settings_name+"/window_geometry", self._window.geometry())

	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):
		"""Watch window events"""

		# Watch for window moves and resizes
		if watched == self._window and event.type() in (QtCore.QEvent.Type.Resize, QtCore.QEvent.Type.Move, QtCore.QEvent.Type.FocusIn):
			print("YAS")
			self._timer_window_geometry.start()

		return super().eventFilter(watched, event)