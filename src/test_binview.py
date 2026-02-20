import sys
from PySide6 import QtWidgets

from binspector.binview  import binviewitemtypes, binviewmodel
from binspector.binitems import binitemsmodel, binitemtypes
from binspector.textview import textviewmodel, textviewproxymodel

from binspector.vieweditor import editorwidget
from binspector.textview import textview
from binspector.models import viewmodels
import avb


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_editor = editorwidget.BSBinViewColumnEditor()

	
	tree_binviewer = textview.BSBinTextView()


	with avb.open(sys.argv[1]) as bin_handle:
		bin_view_info = binviewitemtypes.BSBinViewInfo.from_binview(bin_handle.content.view_setting)
	
	bin_view_model = binviewmodel.BSBinViewModel(bin_view_info)

	bin_textview_model = textviewmodel.BSTextViewModel()
	bin_textview_model.setBinViewModel(bin_view_model)
	bin_textview_proxy_model = textviewproxymodel.BSBTextViewSortFilterProxyModel()
	bin_textview_proxy_model.setSourceModel(bin_textview_model)

	#
	tree_binviewer.setModel(bin_textview_proxy_model)
	bin_textview_proxy_model.headerDataChanged.connect(print)
	
	wnd_editor.setBinViewModel(bin_view_model)
	wnd_editor.show()

	tree_binviewer.show()

	app.exec()