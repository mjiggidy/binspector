import sys, pathlib
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.binviewprovider.providermodel import BSBinViewProviderModel
from binspector.binviewprovider import binviewsources
from binspector.binview import binviewitemtypes
from binspector.widgets import binviewcombobox

PATH = "/Users/mjordan/Library/Application Support/GlowingPixel/Binspector/binviews"

if __name__ == "__main__":

#	if not len(sys.argv) > 1:
#		sys.exit(f"Usage: {pathlib.Path(__file__).name} bin.avb")

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	model_files = QtWidgets.QFileSystemModel()
	model_files.setFilter(
		QtCore.QDir.Filter.Files | \
		QtCore.QDir.Filter.NoDotAndDotDot
	)

	model_provider = BSBinViewProviderModel(storage_model=model_files)
#	model_provider.addSessionBinViewSource(
#		binviewsources.BSBinViewSourceBin(
#			binviewitemtypes.BSBinViewInfo(
#				"HeeHee",
#				[]
#			)
#		)
#	)
	
	idx_current_path = model_files.setRootPath(PATH)

	list_files = binviewcombobox.BSBinViewSelectorComboBox(binview_provider=model_provider)
	list_files.setModel(model_provider)
	#list_files.setRootIndex(idx_current_path)
	list_files.show()

	sys.exit(app.exec())