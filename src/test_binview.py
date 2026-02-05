import sys
from PySide6 import QtWidgets

from binspector.binview import binviewmodel, binviewitems
from binspector.vieweditor import editorwidget
from binspector.textview import textview
from binspector.models import viewmodels, viewmodelitems
import avb


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_editor = editorwidget.BSBinViewColumnEditor()

	
	wnd_bin = textview.BSBinTextView()

	bin_item_model = viewmodels.BSBinItemViewModel()
	
	wnd_bin.model().setSourceModel(bin_item_model)


	with avb.open(sys.argv[1]) as bin_handle:
		bin_view_info = binviewitems.BSBinViewInfo.from_binview(bin_handle.content.view_setting)
	
	bin_view_model = binviewmodel.BSBinViewModel(bin_view_info)
	bin_item_model.setBinViewModel(bin_view_model)


	
	wnd_editor.setBinViewModel(bin_view_model)
	wnd_editor.show()

	wnd_bin.show()

	app.exec()