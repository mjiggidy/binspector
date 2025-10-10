"""
Main app controller
"""
import logging
from PySide6 import QtCore, QtWidgets
from os import PathLike

from ..managers import actions, windows
from . import settings
from ..widgets import mainwindow, menus

class BSMainApplication(QtWidgets.QApplication):
	"""Main application"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setApplicationName("Binspector")
		self.setApplicationVersion("0.0.1")
		self.setQuitOnLastWindowClosed(False)
		self.setStyle("Fusion")

		self.setOrganizationName("GlowingPixel")
		self.setOrganizationDomain("com.glowingpixel")
		self.setDesktopFileName(self.organizationDomain() + "." + self.applicationName())

		# Setup local storage
		self._localStoragePath = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation)
		if not QtCore.QDir().mkpath(self._localStoragePath):
			import sys
			sys.exit(f"Cannot set up local storage path at {self._localStoragePath}")
		
		# Setup logging
		logging.basicConfig(filename=QtCore.QDir(self._localStoragePath).filePath("bs_main.log"), level=logging.DEBUG)

		# Setup settings
		self._settingsManager = settings.BSSettingsManager(
			format   = QtCore.QSettings.Format.IniFormat,
			basepath = self.localStoragePath()
		)
		
		# Setup default menu bar/actions (for macOS when no bin windows are open)
		self._actionmanager = actions.ActionsManager()
		self._default_menubar = menus.DefaultMenuBar(self._actionmanager)
		self._actionmanager.newWindowAction().triggered.connect(self.createMainWindow)
		self._actionmanager.fileBrowserAction().triggered.connect(lambda: self.createMainWindow(show_file_browser=True))
		self._actionmanager.quitApplicationAction().triggered.connect(self.exit)
		
		# Setup window manager
		self._binwindows_manager = windows.BSWindowManager()

	def localStoragePath(self) -> PathLike[str]:
		"""Get the local user storage path"""

		return self._localStoragePath
	
	def settingsManager(self) -> settings.BSSettingsManager:
		return self._settingsManager
	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def createMainWindow(self, show_file_browser:bool=False) -> mainwindow.BSMainWindow:
		"""Create a main window"""
		
		window = self._binwindows_manager.createMainWindow()

		window.setActionsManager(actions.ActionsManager(window))
		window.setSettings(self._settingsManager.settings("bs_main"))
		
		# Connect signals/slots
		window.sig_request_new_window.connect(self.createMainWindow)
		window.sig_request_quit_application.connect(self.exit)
		
		logging.getLogger(__name__).debug("Created %s", window)
		
		window.show()

		if show_file_browser:
			window.browseForBin()

		return window