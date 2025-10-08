from PySide6 import QtCore, QtWidgets
from os import PathLike
from ..core import actions
from ..managers import binproperties
from ..widgets import binwidget

class BSMainWindow(QtWidgets.QMainWindow):
	"""Main window for BinSpectre 👻"""

	def __init__(self):

		super().__init__()

		self._settings = QtCore.QSettings()
		self._actions  = actions.ActionsManager()

		self._man_binview      = binproperties.BSBinViewManager()
		self._man_siftsettings = binproperties.BSBinSiftSettingsManager()
		self._man_appearance   = binproperties.BSBinAppearanceSettingsManager()
		self._man_sorting      = binproperties.BSBinSortingPropertiesManager()
		self._man_binitems     = binproperties.BSBinItemsManager()

		self._bin = binwidget.BSBinContentsWidget()
		
		self.setupWidgets()
		self.setupSignals()
	
	def setupWidgets(self):
		
		self.setCentralWidget(self._bin)
	
	def setupSignals(self):
		pass
		#self._bin.sig_request_open_bin.connect(self.browseForBin)

	def setActionsManager(self, actions:actions.ActionsManager):
		self._actions_manager = actions
	
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

		self.setWindowFilePath(bin_path)