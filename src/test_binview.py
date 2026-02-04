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

	wnd_test = editorwidget.BSBinViewColumnEditor()

	

	bin_window = textview.BSBinTextView()


	with avb.open(sys.argv[1]) as bin_handle:
		bin_view_info = binviewitems.BSBinViewInfo.from_binview(bin_handle.content.view_setting)
	
	bin_view_model = binviewmodel.BSBinViewModel(bin_view_info)


	
	wnd_test.setBinViewModel(bin_view_model)
	wnd_test.show()

	app.exec()