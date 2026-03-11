import sys
import avb
from PySide6 import QtCore, QtWidgets

from binspector.binview import binviewsprovider, binviewsources, binviewitemtypes

# Hack me bra
DEFAULT_FOLDER       = "/Users/mjordan/Library/Application Support/GlowingPixel/Binspector/binviews"
SUPPORTED_FILE_TYPES = ["*.json", "*.avb"]

class BinViewSelectorWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._cmb_binviews = QtWidgets.QComboBox()
		self.layout().addWidget(self._cmb_binviews)

	def comboBox(self) -> QtWidgets.QComboBox:
		
		return self._cmb_binviews

if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_selector = BinViewSelectorWidget()
	wnd_selector.show()

	binviewprovider = binviewsprovider.BSBinViewProviderModel()

	wnd_selector.comboBox().setModel(binviewprovider)

	source_folders = sys.argv[1:] if len(sys.argv) > 1 else [DEFAULT_FOLDER]

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

						binviewprovider.addSessionBinView(
							binviewsources.BSBinViewSourceBin(
								binviewitemtypes.BSBinViewInfo.from_binview(
									bin_handle.content.view_setting
								)
							)
						)

			else:

				binviewprovider.addStoredBinView(
					binviewsources.BSBinViewSourceFile(
						source_file.filePath(), source_file.completeBaseName()
					)
				)
						


	sys.exit(app.exec())