from PySide6 import QtCore, QtWidgets
from os import PathLike
from ..managers import actions, binproperties
from ..widgets import binwidget, menus, toolboxes

class BSMainWindow(QtWidgets.QMainWindow):
	"""Main window for BinSpectre 👻"""

	sig_request_new_window = QtCore.Signal()
	sig_request_quit_application = QtCore.Signal()

	def __init__(self):

		super().__init__()
		
		self._threadpool       = QtCore.QThreadPool()

		self._settings         = QtCore.QSettings()
		self._man_actions      = actions.ActionsManager()

		# Define Managers
		self._man_binview      = binproperties.BSBinViewManager()
		self._man_siftsettings = binproperties.BSBinSiftSettingsManager()
		self._man_appearance   = binproperties.BSBinAppearanceSettingsManager()
		self._man_sorting      = binproperties.BSBinSortingPropertiesManager()
		self._man_binitems     = binproperties.BSBinItemsManager()

		# Define widgets
		self._bin_main         = binwidget.BSBinContentsWidget()

		self._tool_bindisplay  = toolboxes.BSBinDisplaySettingsView()
		self._dock_bindisplay  = QtWidgets.QDockWidget("Bin Display Settings")
		
		self._tool_sifting     = toolboxes.BSBinSiftSettingsView()
		self._dock_sifting     = QtWidgets.QDockWidget("Sift Settings")

		self._tool_appearance  = toolboxes.BSBinAppearanceSettingsView()
		self._dock_appearance  = QtWidgets.QDockWidget("Font Colors")

		self._tool_binview     = QtWidgets.QWidget()
		self._dock_binview     = QtWidgets.QDockWidget("Bin View Settings")
		
		# The rest
		
		self.setMenuBar(menus.BinWindowMenuBar(self._man_actions))
		self.setupWidgets()
		self.setupDock()
		self.setupActions()
		self.setupSignals()


	def setupWidgets(self):
		
		self.setCentralWidget(self._bin_main)

		self._dock_bindisplay.setWidget(self._tool_bindisplay)
		self._dock_sifting.setWidget(self._tool_sifting)
		self._dock_appearance.setWidget(self._tool_appearance)

	def setupDock(self):
		
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_binview)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_bindisplay)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_sifting)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_appearance)

	def setupActions(self):

		self.addAction(self._man_actions.fileBrowserAction())
		self.addAction(self._man_actions.newWindowAction())
		self.addAction(self._man_actions.closeWindowAction())
		self.addAction(self._man_actions.quitApplicationAction())
		
	def setupSignals(self):
		
		self._man_actions.fileBrowserAction().triggered.connect(self.browseForBin)
		self._man_actions.newWindowAction().triggered.connect(self.sig_request_new_window)
		self._man_actions.closeWindowAction().triggered.connect(self.close)
		self._man_actions.quitApplicationAction().triggered.connect(self.sig_request_quit_application)

		# NOTE: Actions have a toggleViewAction() but eh
		self._man_actions.showBinDisplaySettings().toggled.connect(
			lambda t: self._dock_bindisplay.show() if t else self._dock_bindisplay.close()
		)

		self._man_actions.showBinAppearanceSettings().toggled.connect(
			lambda t: self._dock_appearance.show() if t else self._dock_appearance.close()
		)

		self._man_actions.showBinSiftSettings().toggled.connect(
			lambda t: self._dock_sifting.show() if t else self._dock_sifting.close()
		)

		self._man_actions.showBinViewSettings().toggled.connect(
			lambda t: self._dock_binview.show() if t else self._dock_binview.close()
		)

	def setActionsManager(self, actions:actions.ActionsManager):
		self._man_actions = actions
	
	def actionsManager(self) -> actions.ActionsManager:
		return self._man_actions
	
	def setSettings(self, settings:QtCore.QSettings):
		self._settings = settings

	def binViewManager(self) -> binproperties.BSBinViewManager:
		return self._man_binview
	
	def siftSettingsManager(self) -> binproperties.BSBinSiftSettingsManager:
		return self._man_siftsettings
	
	def appearanceManager(self) -> binproperties.BSBinAppearanceSettingsManager:
		return self._man_appearance
	
	def sortingManager(self) -> binproperties.BSBinSortingPropertiesManager:
		return self._man_sorting
	
	def binItemsManager(self) -> binproperties.BSBinItemsManager:
		return self._man_binitems
	
	@QtCore.Slot()
	def browseForBin(self):
		"""Show the file browser to select a bin"""

		file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose an Avid bin...", filter="Avid Bin (*.avb);;All Files (*)", dir=self.windowFilePath())
		
		if file_path:
			self.loadBinFromPath(file_path)

	@QtCore.Slot(object)
	def loadBinFromPath(self, bin_path:PathLike):
		"""Load a bin from the given path"""

		from ..core import binloader

		loader = binloader.BSBinViewLoader(bin_path)
		
		loader.signals().sig_got_view_settings.connect(print)
		loader.signals().sig_got_mob.connect(print)

		self._threadpool.start(loader)
		
		self.setWindowFilePath(bin_path)