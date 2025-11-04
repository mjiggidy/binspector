"""
Main app controller
"""
import logging
from PySide6 import QtCore, QtGui, QtWidgets
from os import PathLike

from . import settings
from ..managers import windows, software_updates
from ..widgets import mainwindow, logwidget, settingswindow
from ..models import logmodels

class BSMainApplication(QtWidgets.QApplication):
	"""Main application"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setApplicationName("Binspector")
		self.setApplicationVersion("0.0.7")
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
		logging.basicConfig(level=logging.DEBUG)

		file_formatter = logging.Formatter("\t".join([
			"%(levelname)s",
			"%(asctime)s",
			"%(name)s",
			"%(message)s"
		]))

		from logging import handlers
		file_handler = handlers.RotatingFileHandler(
			filename    = QtCore.QDir(self._localStoragePath).filePath("bs_main.log"),
			maxBytes    = 1_000_000,
			backupCount = 5,
		)

		file_handler.setFormatter(file_formatter)
		file_handler.setLevel(logging.NOTSET)
		logging.getLogger().addHandler(file_handler)

		import qtlogrelay
		self._qt_log_handler = qtlogrelay.QtLogRelayHandler()
		logging.getLogger().addHandler(self._qt_log_handler)

		self._qt_log_model = logmodels.BSLogDataModel()
		self._qt_log_handler.logEventReceived.connect(self._qt_log_model.addLogRecord, QtCore.Qt.ConnectionType.QueuedConnection)

		self._wnd_log_viewer = None

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
		# TODO: This is bad lol
		self._binwindows_manager.windowGeometryWatcher().sig_window_geometry_changed.connect(lambda: self._settingsManager.setLastWindowGeometry(self.activeWindow().geometry()))

		# Setup updates manager
		self._disable_updates_counter = 0
		self._updates_manager = software_updates.BSUpdatesManager()
		self._updates_manager.setAutoCheckEnabled(self._settingsManager.softwareUpdateAutocheckEnabled())
		self._updates_manager.sig_newReleaseAvailable.connect(self.showUpdatesWindow)
		self._updates_manager.sig_autoCheckChanged.connect(self._settingsManager.setSoftwareUpdateAutocheckEnabled)
		self._wnd_update = None	# Window will be created in `self.showUpdatesWindow`

		# Settings Temp
		self._wnd_settings = settingswindow.BSSettingsPanel()
		self._wnd_settings.setUseAnimations(self._settingsManager.useFancyProgressBar())
		self._wnd_settings.setMobQueueSize(self._settingsManager.mobQueueSize())
		self._wnd_settings.sig_use_animations_changed.connect(self._settingsManager.setUseFancyProgressBar)
		self._wnd_settings.sig_use_animations_changed.connect(lambda use_animation: [w.setUseAnimation(use_animation) for w in self._binwindows_manager.windows()])
		self._wnd_settings.sig_mob_queue_size_changed.connect(self._settingsManager.setMobQueueSize)
		self._wnd_settings.sig_mob_queue_size_changed.connect(lambda queue_size: [w.setMobQueueSize(queue_size) for w in self._binwindows_manager.windows()])
		self._wnd_settings.setWindowTitle("Temp Settings")
		self._wnd_settings.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self._wnd_settings.show()

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

		if current_window := self.activeWindow():
			start_geo = current_window.geometry().translated(QtCore.QPoint(10,10))
		elif saved_geo := self._settingsManager.lastWindowGeometry():
			start_geo = saved_geo
		else:
			start_geo = QtCore.QRect(QtCore.QPoint(0,0), QtCore.QSize(1024,480)).translated(QtCore.QPoint(800,800))
		
		window:mainwindow.BSMainWindow = self._binwindows_manager.addWindow(mainwindow.BSMainWindow())

		window.setGeometry(start_geo)

		#window.setActionsManager(actions.ActionsManager(window))
		#window.setSettings(self._settingsManager.settings("bs_main"))
		
		# Connect signals/slots
		# TODO: Probably connect this directly to managers, like binViewManager below
		# The window shouldn't have to care much about emitting all these signals, I don't think
		window.sig_request_new_window.connect(self.createMainWindow)
		window.sig_request_quit_application.connect(self.exit)
		window.sig_request_show_log_viewer.connect(self.showLogWindow)
		window.sig_request_show_user_folder.connect(self.showLocalStorage)
		window.sig_request_visit_discussions.connect(lambda: QtGui.QDesktopServices.openUrl("https://github.com/mjiggidy/binspector/discussions/"))
		window.sig_request_check_updates.connect(self.showUpdatesWindow)
		window.sig_bin_changed.connect(self._settingsManager.setLastBinPath)

		# Restore Toggle Settings
		window.binViewManager().setBinViewEnabled(self._settingsManager.binViewIsEnabled())
		window.binViewManager().sig_view_mode_toggled.connect(self._settingsManager.setBinViewEnabled)
		
		window.binViewManager().setBinFiltersEnabled(self._settingsManager.binFiltersEnabled())
		window.binViewManager().sig_bin_filters_toggled.connect(self._settingsManager.setBinFiltersEnabled)

		window.appearanceManager().setEnableBinAppearance(self._settingsManager.binAppearanceIsEnabled())
		window.appearanceManager().sig_bin_appearance_toggled.connect(self._settingsManager.setBinAppearanceEnabled)

		window.setMobQueueSize(self._settingsManager.mobQueueSize())
		window.setUseAnimation(self._settingsManager.useFancyProgressBar())

		window.binLoadingSignalManger().sig_begin_loading.connect(self.setUpdateCheckDisabled)
		window.binLoadingSignalManger().sig_done_loading.connect(self.setUpdateCheckEnabled)

		logging.getLogger(__name__).debug("Created %s", window.winId())
		
		window.show()
		#window.raise_()
		#window.activateWindow()
		self.setActiveWindow(window)

		if show_file_browser:
			window.showFileBrowser(
				self._settingsManager.lastBinPath() or QtCore.QDir.homePath()
			)

		return window
	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def setUpdateCheckEnabled(self, is_enabled:bool=True):

		self._updates_manager.setEnabled(bool(is_enabled))

		self._disable_updates_counter = max(self._disable_updates_counter + (-1 if is_enabled else 1), 0)

		logging.getLogger(__name__).debug("_disable_updates_counter = %s", self._disable_updates_counter)

		if self._disable_updates_counter:
			self._updates_manager.setDisabled()
		else:
			self._updates_manager.setEnabled()

	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def setUpdateCheckDisabled(self, is_disabled:bool=True):

		self.setUpdateCheckEnabled(not bool(is_disabled))
	
	@QtCore.Slot()
	def showLogWindow(self):

		if not self._wnd_log_viewer:

			self._wnd_log_viewer = logwidget.BSLogViewerWidget()
			self._wnd_log_viewer.setWindowTitle("Log Viewer")
			self._wnd_log_viewer.setWindowFlag(QtCore.Qt.WindowType.Tool)

			start_geo = self.activeWindow().geometry().translated(QtCore.QPoint(100,100)) if self.activeWindow() else self._wnd_log_viewer.geometry()
			start_geo.setSize(QtCore.QSize(900,200))
			self._wnd_log_viewer.setGeometry(start_geo)
			
			self._wnd_log_viewer.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			self._wnd_log_viewer.destroyed.connect(lambda: setattr(self, "_wnd_log_viewer", None))
			
			self._wnd_log_viewer.treeView().setModel(self._qt_log_model)
		
		self._wnd_log_viewer.show()
		self._wnd_log_viewer.activateWindow()

	
	@QtCore.Slot()
	def showUpdatesWindow(self):

		from ..widgets import software_updates
		
		# Create window if it's not already open
		if not self._wnd_update:

			self._wnd_update = software_updates.BSCheckForUpdatesWindow()
			
			self._wnd_update.setWindowFlag(QtCore.Qt.WindowType.Tool)
			self._wnd_update.setUpdateManager(self.updatesManager())
			self._wnd_update.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			
			# Release dat ref
			self._wnd_update.destroyed.connect(lambda: setattr(self, "_wnd_update", None))

		# Check for updates at window launch if an update hasn't already been found
		if self._updates_manager.latestReleaseInfo() is None:
			self._updates_manager.checkForUpdates()
		else:
			logging.getLogger(__name__).debug("Latest release info = %s", self._updates_manager.latestReleaseInfo())

		self._wnd_update.show()
		self._wnd_update.raise_()
		self._wnd_update.activateWindow()
		self._wnd_update.setFocus(QtCore.Qt.FocusReason.PopupFocusReason) # Not sure if want