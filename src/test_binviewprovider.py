import sys
import avb
from PySide6 import QtCore, QtWidgets

from binspector.binview import binviewitemtypes
from binspector.binviewprovider import binviewsources, providermodel, providerstorage
from binspector.widgets import binviewcombobox

# Hack me bra
DEFAULT_FOLDER       = "/Users/mjordan/Library/Application Support/GlowingPixel/Binspector"
SUPPORTED_FILE_TYPES = ["*.avb"]

class BinViewSelectorWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._cmb_binviews = binviewcombobox.BSBinViewSelectorComboBox()
		self.layout().addWidget(self._cmb_binviews)

	def comboBox(self) -> binviewcombobox.BSBinViewSelectorComboBox:
		
		return self._cmb_binviews
	
@QtCore.Slot(object)
def updateBinViewFileList(binview_sources:list[binviewsources.BSBinViewSourceFile]):

	binview_provider_model.clearStoredViews()
	
	for binview_source_info in binview_sources:
		
		binview_provider_model.addStoredBinView(binview_source_info)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_selector = BinViewSelectorWidget()
	wnd_selector.show()

	binview_provider_model = providermodel.BSBinViewProviderModel()

	folder_watcher = providerstorage.BSBinViewStorageManager(parent=app, base_path=DEFAULT_FOLDER)
	folder_watcher.setRefreshInterval(5_000)
	folder_watcher.sig_binviews_refreshed.connect(updateBinViewFileList)

	updateBinViewFileList(folder_watcher.lastBinViews())

	source_folders = sys.argv[1:] if len(sys.argv) > 1 else []

	for source_folder in source_folders:

		source_folder_iter = QtCore.QDirIterator(
			source_folder,
			SUPPORTED_FILE_TYPES,
			QtCore.QDir.Filter.NoDotAndDotDot|QtCore.QDir.Filter.Files|QtCore.QDir.Filter.Readable,
			QtCore.QDirIterator.IteratorFlag.FollowSymlinks|QtCore.QDirIterator.IteratorFlag.Subdirectories
		)

		while source_folder_iter.hasNext():

			source_file = source_folder_iter.nextFileInfo()

			print("Adding ", source_file)
			
			if source_file.suffix().lower() == "avb":

					with avb.open(source_file.filePath()) as bin_handle:

						binview_provider_model.addSessionBinView(
							binviewsources.BSBinViewSourceBin(
								binviewitemtypes.BSBinViewInfo.from_binview(
									bin_handle.content.view_setting
								)
							)
						)


						
	wnd_selector.comboBox().setModel(binview_provider_model)

	sys.exit(app.exec())