"""
Window managers
"""

import weakref, logging
from PySide6 import QtCore, QtGui, QtWidgets

class BSWindowManager(QtCore.QObject):
	"""Main window manager (for scoping etc)"""

	# This is done by maintaining a set of weakrefs

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._window_refs:set[weakref.ReferenceType[QtWidgets.QWidget]] = set()
		self._last_active_ref = None
		self._window_geometry_watcher = BSWindowGeometryWatcher()

		self._window_geometry_watcher.sig_window_has_focus.connect(self._setLastActiveBinWindow)
		

	def _setLastActiveBinWindow(self, wnd:QtWidgets.QWidget):

		for wnd_ref in self._window_refs:
			
			if wnd_ref() == wnd:
				
				logging.getLogger(__name__).debug("Setting last active bin window: %s", wnd)
				self._last_active_ref = wnd_ref
				return
			
		logging.getLogger(__name__).warning("Newly-active window not in weakrefs...")
	
	def lastActiveBinWindow(self) -> QtWidgets.QWidget|None:

		return self._last_active_ref() if self._last_active_ref else None
	
	def addWindow(self, window:QtWidgets.QWidget) -> QtWidgets.QWidget:
		"""Add an existing window (and returns it again, unchanged)"""
		
		win_weakref = weakref.ref(window)

		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		window.installEventFilter(self._window_geometry_watcher)
		window.destroyed.connect(lambda: self._removeWindowRef(win_weakref))

		self._window_refs.add(win_weakref)

		logging.getLogger(__name__).debug("Created new window (windows_list=%s)", self.windows())

		return window
	
	def windowGeometryWatcher(self) -> "BSWindowGeometryWatcher":
		return self._window_geometry_watcher
	
	def windows(self) -> list[QtWidgets.QWidget]:
		return [w() for w in self._window_refs if w()]
	
	@QtCore.Slot(object)
	def _removeWindowRef(self, window_ref:weakref.ReferenceType[QtWidgets.QWidget]):

		try:
			self._window_refs.discard(window_ref)
		
		except Exception as e:
			logging.getLogger(__name__).warning("Strange thing while closing window: %s (window list length=%s)", e, len(self._window_refs))






class BSWindowGeometryWatcher(QtCore.QObject):
	"""Watch windows for changes"""

	sig_window_geometry_changed = QtCore.Signal()
	sig_window_has_focus        = QtCore.Signal(object)

	def __init__(self, timeout_ms:int=200, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._timer_window_geometry = QtCore.QTimer(singleShot=True, interval=timeout_ms)
		self._timer_window_geometry.timeout.connect(self.sig_window_geometry_changed)
	
	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):
		"""Watch window events"""

		# Watch for window moves and resizes
		if event.type() in (QtCore.QEvent.Type.Resize, QtCore.QEvent.Type.Move, QtCore.QEvent.Type.FocusIn):
			self._timer_window_geometry.start()

		if event.type() == QtCore.QEvent.Type.WindowActivate:
			self.sig_window_has_focus.emit(watched)


		return super().eventFilter(watched, event)







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
			self._timer_window_geometry.start()

		return super().eventFilter(watched, event)