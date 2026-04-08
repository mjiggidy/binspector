import sys
from PySide6 import QtCore, QtWidgets

from binspector.binview  import binviewitemtypes, binviewmodel, jsonadapter
from binspector.binitems import binitemsmodel
from binspector.textview import bincompositemodel
from binspector.core import binparser

from binspector.vieweditor import editorwidget
from binspector.textview import textview

from binspector.binfilters import binviewproxymodel, bindisplayproxymodel

import avb, avbutils



@QtCore.Slot(dict)
def exportJson():

	binview_info = bin_view_model.binViewInfo()
	with open(binview_info.name + ".json", "w") as view_handle:

		print(jsonadapter.BSBinViewJsonAdapter.from_binview(binview_info), file=view_handle)
		print("Written to", view_handle.name)

def loadFromBinPath(bin_path):
		
	if bin_path.casefold().endswith(".avb"):
		
		with avb.open(bin_path) as bin_handle:
			bin_view_model.setBinViewInfo(binviewitemtypes.BSBinViewInfo.from_binview(bin_handle.content.view_setting))

			for idx, item in enumerate(bin_handle.content.items):
				thing = binparser.load_item_from_bin(item)
				bin_item_model.addBinItem(thing)
	

	elif bin_path.casefold().endswith(".json"):

		with open(sys.argv[1]) as view_handle:
			bin_view_model.setBinViewInfo(jsonadapter.BSBinViewJsonAdapter.to_binview(view_handle.read()))

	
if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_editor = editorwidget.BSBinViewColumnEditor()

	

	bin_view_model      = binviewmodel.BSBinViewModel()
	bin_item_model      = binitemsmodel.BSBinItemModel()

	bin_item_filter     = bindisplayproxymodel.BSBinDisplayFilterProxyModel(bin_items_model=bin_item_model)
	bin_view_filter     = binviewproxymodel.BSBinViewFilterProxyModel(bin_columns_model=bin_view_model)

	bin_composite_model = bincompositemodel.BSBinCompositeModel(item_model=bin_item_filter, view_model=bin_view_filter)

	final_proxy         = QtCore.QIdentityProxyModel()
	final_proxy.setSourceModel(bin_composite_model)
	
	###
	
	loadFromBinPath(sys.argv[1])
	
	wnd_editor.setBinViewModel(bin_view_model)
	wnd_editor.show()

	tree_binviewer = textview.BSBinTextView()
	tree_binviewer.setModel(final_proxy)
	tree_binviewer.move(wnd_editor.geometry().topRight() + QtCore.QPoint(100,0))
	tree_binviewer.show()

	#bin_item_filter.setAcceptedItemTypes(avbutils.bins.BinDisplayItemTypes.SOURCE)

	wnd_editor.sig_export_binview_requested.connect(exportJson)

	print(bin_item_filter.rowCount(QtCore.QModelIndex()))
	

	app.exec()