"""
Main app controller
"""
import logging
from PySide6 import QtCore, QtGui, QtWidgets
from os import PathLike

from . import settings
from ..managers import windows, software_updates
from ..widgets import mainwindow

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
		# NOTE: This is currently clumsy and weird.  I'll uh, come back to this
#		self.setQuitOnLastWindowClosed(False)
#		self._actionmanager = actions.ActionsManager()
#		self._default_menubar = menus.DefaultMenuBar(self._actionmanager)
#		self._actionmanager.newWindowAction().triggered.connect(self.createMainWindow)
#		self._actionmanager.fileBrowserAction().triggered.connect(lambda: self.createMainWindow(show_file_browser=True))
#		self._actionmanager.quitApplicationAction().triggered.connect(self.exit)
		
		# Setup window manager
		self._binwindows_manager = windows.BSWindowManager()

		# Setup updates manager
		self._updates_manager = software_updates.BSUpdatesManager()
		self._updates_manager.sig_newReleaseAvailable.connect(self.showUpdatesWindow)

	def localStoragePath(self) -> PathLike[str]:
		"""Get the local user storage path"""

		return self._localStoragePath
	
	def showLocalStorage(self):
		"""Open local user storage folder"""

		QtGui.QDesktopServices.openUrl(
			QtCore.QUrl.fromLocalFile(self.localStoragePath())
		)
	
	def settingsManager(self) -> settings.BSSettingsManager:
		return self._settingsManager
	
	def updatesManager(self) -> software_updates.BSUpdatesManager:
		return self._updates_manager
	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def createMainWindow(self, show_file_browser:bool=False) -> mainwindow.BSMainWindow:
		"""Create a main window"""
		
		window = self._binwindows_manager.addWindow(mainwindow.BSMainWindow())

		#window.setActionsManager(actions.ActionsManager(window))
		#window.setSettings(self._settingsManager.settings("bs_main"))
		
		# Connect signals/slots
		window.sig_request_new_window.connect(self.createMainWindow)
		window.sig_request_quit_application.connect(self.exit)
		window.sig_request_show_user_folder.connect(self.showLocalStorage)
		window.sig_request_visit_discussions.connect(lambda: QtGui.QDesktopServices.openUrl("https://github.com/mjiggidy/binspector/discussions/"))
		window.sig_request_check_updates.connect(self.showUpdatesWindow)
		
		logging.getLogger(__name__).debug("Created %s", window)
		window.show()

		if show_file_browser:
			window.showFileBrowser()

		return window
	
	@QtCore.Slot()
	def showUpdatesWindow(self):

		from ..widgets import software_updates
		
		try:
			self._wnd_update.show()
			self._wnd_update.setFocus(QtCore.Qt.FocusReason.PopupFocusReason)
		
		except Exception as e:
			#print(e)
			self._wnd_update = software_updates.BSCheckForUpdatesWindow()
			
			self._wnd_update.setWindowFlag(QtCore.Qt.WindowType.Tool)
			self._wnd_update.setUpdateManager(self.updatesManager())
			self._wnd_update.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			self._wnd_update.destroyed.connect(lambda: setattr(self, "_wnd_update", None))

			self._wnd_update.show()
