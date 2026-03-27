import sys, typing
from PySide6 import QtCore, QtWidgets

from binspector.binview  import binviewitemtypes, binviewmodel, jsonadapter
from binspector.binitems import binitemsmodel, binitemtypes
from binspector.textview import textviewmodel, textviewproxymodel

from binspector.vieweditor import editorwidget
from binspector.textview import textview
import avb

bin_view_model = binviewmodel.BSBinViewModel()

@QtCore.Slot(dict)
def exportJson():

	binview_info = bin_view_model.binViewInfo()
	with open(binview_info.name + ".json", "w") as view_handle:

		print(jsonadapter.BSBinViewJsonAdapter.from_binview(binview_info), file=view_handle)
		print("Written to", view_handle.name)

	
if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_editor = editorwidget.BSBinViewColumnEditor()

	
	tree_binviewer = textview.BSBinTextView()




	if sys.argv[1].lower().endswith(".avb"):
		
		with avb.open(sys.argv[1]) as bin_handle:
			bin_view_model.setBinViewInfo(binviewitemtypes.BSBinViewInfo.from_binview(bin_handle.content.view_setting))

	elif sys.argv[1].lower().endswith(".json"):

		with open(sys.argv[1]) as view_handle:
			bin_view_model.setBinViewInfo(jsonadapter.BSBinViewJsonAdapter.to_binview(view_handle.read()))

	bin_textview_model = textviewmodel.BSTextViewModel()
	bin_textview_model.setBinViewModel(bin_view_model)
	bin_textview_proxy_model = textviewproxymodel.BSBTextViewSortFilterProxyModel()
	bin_textview_proxy_model.setSourceModel(bin_textview_model)
#
	#
	tree_binviewer.setModel(bin_textview_proxy_model)
	bin_textview_proxy_model.headerDataChanged.connect(lambda h: print("Header data changed: ", h))
	
	wnd_editor.setBinViewModel(bin_view_model)
	wnd_editor.show()
	tree_binviewer.move(wnd_editor.geometry().topRight() + QtCore.QPoint(100,0))

	tree_binviewer.show()

	wnd_editor.sig_export_binview_requested.connect(exportJson)
	

	app.exec()