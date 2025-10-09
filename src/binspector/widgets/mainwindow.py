from PySide6 import QtCore, QtWidgets
from os import PathLike
from ..managers import actions
from ..managers import binproperties
from ..widgets import binwidget, menus

class BSMainWindow(QtWidgets.QMainWindow):
	"""Main window for BinSpectre 👻"""

	sig_request_new_window = QtCore.Signal()
	sig_request_quit_application = QtCore.Signal()

	def __init__(self):

		super().__init__()

		self._settings = QtCore.QSettings()
		self._actions  = actions.ActionsManager(parent=self)

		self._man_binview      = binproperties.BSBinViewManager()
		self._man_siftsettings = binproperties.BSBinSiftSettingsManager()
		self._man_appearance   = binproperties.BSBinAppearanceSettingsManager()
		self._man_sorting      = binproperties.BSBinSortingPropertiesManager()
		self._man_binitems     = binproperties.BSBinItemsManager()

		self._bin = binwidget.BSBinContentsWidget()
		
		self.setupWidgets()
		self.setupActions()
		self.setupSignals()

		self.setMenuBar(menus.BinWindowMenuBar(self._actions))
	
	def setupWidgets(self):
		
		self.setCentralWidget(self._bin)
		#self._bin.topSectionWidget().addAction(self._actions.fileBrowserAction())

	def setupActions(self):
		pass
		#self.addAction(self._actions.fileBrowserAction())
	
	def setupSignals(self):
		
		self.addAction(self._actions.fileBrowserAction())
		self._actions.fileBrowserAction().triggered.connect(self.browseForBin)

		self.addAction(self._actions.newWindowAction())
		self._actions.newWindowAction().triggered.connect(self.sig_request_new_window)

		self.addAction(self._actions.closeWindowAction())
		self._actions.closeWindowAction().triggered.connect(self.close)

		self.addAction(self._actions.quitApplicationAction())
		self._actions.quitApplicationAction().triggered.connect(self.sig_request_quit_application)
		

	def setActionsManager(self, actions:actions.ActionsManager):
		self._actions_manager = actions
	
	def actionsManager(self) -> actions.ActionsManager:
		return self._actions_manager
	
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

		binloader.BSBinViewLoader(bin_path)
		
		self.setWindowFilePath(bin_path)