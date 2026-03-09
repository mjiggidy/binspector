import sys, typing
from PySide6 import QtCore, QtWidgets

from binspector.binview  import binviewitemtypes, binviewmodel
from binspector.binitems import binitemsmodel, binitemtypes
from binspector.textview import textviewmodel, textviewproxymodel

from binspector.vieweditor import editorwidget
from binspector.textview import textview
from binspector.models import viewmodels
import avb

@QtCore.Slot(dict)
def exportJson(binview_dict:dict[str, typing.Any]):

	import pathlib, json

	path_output = pathlib.Path("/Users/mjordan/Desktop", binview_dict["name"]+".json")
	
	try:
		with path_output.open("w") as file_binview:
			print(
				json.dumps(binview_dict, indent="\t"),
				file=file_binview
			)
	except Exception as e:
		print("Couldn't: ", e)
	else:
		print(f"Exported to ", path_output)

if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_editor = editorwidget.BSBinViewColumnEditor()

	
	tree_binviewer = textview.BSBinTextView()


	with avb.open(sys.argv[1]) as bin_handle:
		bin_view_info = binviewitemtypes.BSBinViewInfo.from_binview(bin_handle.content.view_setting)
		print("Attributes:", )
		print(list(bin_handle.content.view_setting.attributes.items()))
	
	bin_view_model = binviewmodel.BSBinViewModel(bin_view_info)

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