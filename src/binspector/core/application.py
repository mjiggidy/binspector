"""
Main app controller
"""
import logging
from PySide6 import QtCore, QtWidgets
from os import PathLike

from ..managers import actions
from . import settings
from ..widgets import mainwindow, menus

class BSMainApplication(QtWidgets.QApplication):
	"""Main application"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setApplicationName("Binspector")
		self.setApplicationVersion("0.0.1")
		self.setStyle("Fusion")

		self.setOrganizationName("GlowingPixel")
		self.setOrganizationDomain("com.glowingpixel")
		self.setDesktopFileName(self.organizationDomain() + "." + self.applicationName())

		# NOTE: Need to sus-out ownership stuff if we doin this
		#self.setQuitOnLastWindowClosed(False)
		#self._default_menubar = menus.DefaultMenuBar(actions.ActionsManager(self))

		self._mainwindows:list[mainwindow.BSMainWindow] = []

		self._localStoragePath = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation)
		QtCore.QDir().mkpath(self._localStoragePath)

		logging.basicConfig(filename=QtCore.QDir(self._localStoragePath).filePath("bs_main.log"), level=logging.DEBUG)

		self._settingsManager = settings.BSSettingsManager(
			format   = QtCore.QSettings.Format.IniFormat,
			basepath = self.localStoragePath()
		)

	def localStoragePath(self) -> PathLike[str]:
		"""Get the local user storage path"""
		return self._localStoragePath
	
	def settingsManager(self) -> settings.BSSettingsManager:
		return self._settingsManager
	
	def createMainWindow(self) -> mainwindow.BSMainWindow:
		"""Create a main window"""
		
		window = mainwindow.BSMainWindow()
		
		# Scope!
		self._mainwindows.append(window)
		#window.destroyed.connect(lambda: print(f"{self._mainwindows.remove(window)} {self._mainwindows}"))

		window.setActionsManager(actions.ActionsManager(window))
		window.setSettings(self._settingsManager.settings("bs_main"))
		
		window.sig_request_new_window.connect(self.createMainWindow)
		window.sig_request_quit_application.connect(self.closeAllWindows)
		
		logging.getLogger(__name__).debug("Created %s", window)
		
		window.show()
		return window