import sys
from PySide6 import QtWidgets, QtCore

from binspector.binview import binviewmodel, binviewitems
from binspector.vieweditor import editorwidget
from binspector.textview import textview
from binspector.models import viewmodels, viewmodelitems
import avb

@QtCore.Slot(int, int, int)
def headerMoved(idx_logical, idx_old_vis, idx_new_vis):
	
	moved_header_name = wnd_bin.model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, binviewitems.BSBinColumnInfoRole.DisplayNameRole)

	if idx_new_vis > 0:
		leading_header_logical_index = wnd_bin.header().logicalIndex(idx_new_vis-1)
		leading_header_name = wnd_bin.model().headerData(leading_header_logical_index, QtCore.Qt.Orientation.Horizontal, binviewitems.BSBinColumnInfoRole.DisplayNameRole)
		print(f"{moved_header_name} moved after {leading_header_name}")

		# Need to map back to proxy stuff
		new_logical_index = leading_header_logical_index + 1
	
	else:
		print(f"{moved_header_name} moved to front")
		new_logical_index = 0

	print("New logical index: ", new_logical_index)

if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_editor = editorwidget.BSBinViewColumnEditor()

	
	wnd_bin = textview.BSBinTextView()
	
	
	# When section moved via header, find the logical index of the preceding visible visual index
	# And move the BinCOlumnInfo to the next index in the model I think
	wnd_bin.header().sectionMoved.connect(headerMoved)

	bin_item_model = viewmodels.BSBinItemViewModel()
	
	wnd_bin.model().setSourceModel(bin_item_model)


	with avb.open(sys.argv[1]) as bin_handle:
		bin_view_info = binviewitems.BSBinView.from_binview(bin_handle.content.view_setting)
	
	bin_view_model = binviewmodel.BSBinViewModel(bin_view_info)
	bin_item_model.setBinViewModel(bin_view_model)


	
	wnd_editor.setBinViewModel(bin_view_model)
	wnd_editor.show()

	wnd_bin.show()

	app.exec()

