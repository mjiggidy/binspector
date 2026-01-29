import sys
from PySide6 import QtWidgets, QtGui, QtCore

from binspector.binview import binviewmodel
import avb, avbutils


if __name__ == "__main__":

	app = QtWidgets.QApplication()

	wnd_test = QtWidgets.QListView()

	with avb.open(sys.argv[1]) as bin_handle:
		bin_view_info = binviewmodel.BSBinViewInfo.from_binview(bin_handle.content.view_setting)
	
	bin_view_model = binviewmodel.BSBinViewModel(bin_view_info)


	
	wnd_test.setModel(bin_view_model)
	wnd_test.show()

	app.exec()