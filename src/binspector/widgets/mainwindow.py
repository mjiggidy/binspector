from PySide6 import QtCore, QtWidgets
from os import PathLike
from ..managers import actions, binproperties
from ..widgets import binwidget, menus, toolboxes
from ..views import treeview

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
		self._man_bindisplay   = binproperties.BSBinDisplaySettingsManager()

		# Define widgets
		self._bin_main         = binwidget.BSBinContentsWidget()

		self._tool_bindisplay  = toolboxes.BSBinDisplaySettingsView()
		self._dock_bindisplay  = QtWidgets.QDockWidget("Bin Display Settings")
		
		self._tool_sifting     = toolboxes.BSBinSiftSettingsView()
		self._dock_sifting     = QtWidgets.QDockWidget("Sift Settings")

		self._tool_appearance  = toolboxes.BSBinAppearanceSettingsView()
		self._dock_appearance  = QtWidgets.QDockWidget("Font Colors")

		self._tool_binview     = treeview.LBTreeView()
		self._dock_binview     = QtWidgets.QDockWidget("Bin View Settings")
		
		# The rest
		
		self.setMenuBar(menus.BinWindowMenuBar(self._man_actions))
		self.setupWidgets()
		self.setupDock()
		self.setupActions()
		self.setupSignals()


	def setupWidgets(self):
		"""Configure general widget placement and config"""
		
		self.setCentralWidget(self._bin_main)

		self._dock_bindisplay.setWidget(self._tool_bindisplay)
		self._dock_sifting.setWidget(self._tool_sifting)
		self._dock_appearance.setWidget(self._tool_appearance)
		self._dock_binview.setWidget(self._tool_binview)

		self._bin_main.treeView().model().setSourceModel(self._man_binitems.viewModel())
		self._tool_binview.setModel(self._man_binview.viewModel())
		

	def setupDock(self):
		"""Add and prepare the dock"""
		
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_binview)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_bindisplay)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_sifting)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_appearance)

	def setupActions(self):
		"""Add applicable actions"""

		self.addActions(self._man_actions.applicationActionsGroup().actions())
		self.addActions(self._man_actions.fileActionsGroup().actions())
		self.addActions(self._man_actions.windowActionsGroup().actions())
		
		self.addActions(self._man_actions.showBinSettingsActionGroup().actions())
		self.addActions(self._man_actions.viewModesActionGroup().actions())

		
	def setupSignals(self):
		"""Connect signals and slots"""

		# Window/File Actions
		self._man_actions.fileBrowserAction().triggered.connect(self.showFileBrowser)
		self._man_actions.newWindowAction().triggered.connect(self.sig_request_new_window)
		self._man_actions.closeWindowAction().triggered.connect(self.close)
		self._man_actions.quitApplicationAction().triggered.connect(self.sig_request_quit_application)

		# Toolbox Toggle Actions
		# NOTE: Dock widgets have a toggleViewAction() butuhhhhh
		self._man_actions.showBinDisplaySettings().toggled.connect(self._dock_bindisplay.setVisible)
		self._dock_bindisplay.visibilityChanged.connect(self._man_actions.showBinDisplaySettings().setChecked)

		self._man_actions.showBinAppearanceSettings().toggled.connect(self._dock_appearance.setVisible)
		self._dock_appearance.visibilityChanged.connect(self._man_actions.showBinAppearanceSettings().setChecked)

		self._man_actions.showBinSiftSettings().toggled.connect(self._dock_sifting.setVisible)
		self._dock_sifting.visibilityChanged.connect(self._man_actions.showBinSiftSettings().setChecked)

		self._man_actions.showBinViewSettings().toggled.connect(self._dock_binview.setVisible)
		self._dock_binview.visibilityChanged.connect(self._man_actions.showBinViewSettings().setChecked)

		# Bin Settings Toolboxes
		self._man_bindisplay.sig_bin_display_changed.connect(self._tool_bindisplay.setFlags)
		self._man_bindisplay.sig_bin_display_changed.connect(self._bin_main.treeView().model().setBinDisplayItemTypes)
		self._tool_bindisplay.sig_flags_changed.connect(self._man_bindisplay.setBinDisplayFlags)

		self._man_appearance.sig_font_changed.connect(self._tool_appearance.setBinFont)
		self._man_appearance.sig_palette_changed.connect(self._tool_appearance.setBinPalette)
		self._man_appearance.sig_window_rect_changed.connect(self._tool_appearance.setBinRect)
		self._man_appearance.sig_was_iconic_changed.connect(self._tool_appearance.setWasIconic)

		self._man_appearance.sig_palette_changed.connect(self._bin_main.setBinColors)
		self._man_appearance.sig_font_changed.connect(self._bin_main.setBinFont)
		self._tool_appearance.sig_font_changed.connect(self._man_appearance.sig_font_changed)
		self._tool_appearance.sig_palette_changed.connect(self._bin_main.setBinColors)

	##
	## Getters & Setters
	##

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
	
	##
	## Slots
	##
	
	@QtCore.Slot()
	def showFileBrowser(self):
		"""Show the file browser to select a bin"""

		file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose an Avid bin...", filter="Avid Bin (*.avb);;All Files (*)", dir=self.windowFilePath())
		
		if file_path:
			self.loadBinFromPath(file_path)

	@QtCore.Slot(object)
	def loadBinFromPath(self, bin_path:PathLike):
		"""Load a bin from the given path"""

		from ..core import binloader

		loader = binloader.BSBinViewLoader(bin_path)
		
		loader.signals().sig_got_view_settings.connect(self._man_binview.setBinView)
		loader.signals().sig_got_view_settings.connect(self._man_binitems.setBinView)

		loader.signals().sig_got_bin_appearance_settings.connect(self._man_appearance.setAppearanceSettings)
		
		loader.signals().sig_got_bin_display_settings.connect(self._man_bindisplay.setBinDisplayFlags)

		loader.signals().sig_got_mob.connect(self._man_binitems.addMob)

		self._threadpool.start(loader)
		
		self.setWindowFilePath(bin_path)