import avb, avbutils
from PySide6 import QtCore, QtWidgets
from binspector.siftwidget import siftwidget, columnchoosermodel
from binspector.binview import binviewmodel, binviewitemtypes
from binspector.binfilters import binviewproxymodel

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_siftwidget = siftwidget.BSSiftSettingsWidget()

font = wnd_siftwidget.font()
font.setPointSizeF(font.pointSizeF() * 0.8)

wnd_siftwidget.setWindowTitle("Custom Sift")
wnd_siftwidget.setFont(font)
wnd_siftwidget.setWindowFlag(QtCore.Qt.WindowType.Tool)
wnd_siftwidget.show()

geo = wnd_siftwidget.geometry()
geo.setWidth(geo.height() * 1.75)

wnd_siftwidget.setGeometry(geo)
wnd_siftwidget.setFixedHeight(geo.height())

model_binview       = binviewmodel.BSBinViewModel()
model_binviewfilter = binviewproxymodel.BSBinViewFilterProxyModel(bin_columns_model=model_binview)
model_sift_columns  = columnchoosermodel.BSBinSiftColumnChooserModel(bin_view_model=model_binviewfilter)

wnd_siftwidget.setBinViewModel(model_binviewfilter)

import sys
with avb.open(sys.argv[1]) as bin_file:
	
	model_binview.setBinViewInfo(
		binviewitemtypes.BSBinViewInfo.from_binview(bin_file.content.view_setting)
	)
	
	wnd_siftwidget.setSiftOptions([
		avbutils.bins.BinSiftOption.from_sift_item(s) for s in bin_file.content.sifted_settings
	])

app.exec()