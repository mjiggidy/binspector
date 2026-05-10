import avb, avbutils
from PySide6 import QtCore, QtWidgets
from binspector.siftwidget import scopesmodel, siftwidget
from binspector.binview import binviewmodel, binviewitemtypes
from binspector.binfilters import binviewproxymodel
from binspector.binfilters.siftfilter import sifters
from binspector.binitems import binitemtypes

app = QtWidgets.QApplication()
app.setStyle("Fusion")

model_binview       = binviewmodel.BSBinViewModel()
model_binviewfilter = binviewproxymodel.BSBinViewFilterProxyModel(bin_columns_model=model_binview)

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

model_sift_columns  = scopesmodel.BSSiftScopeViewModel(bin_view_model=model_binviewfilter)

wnd_siftwidget.setBinViewModel(model_binviewfilter)

wnd_siftwidget.sig_criteria_set.connect(print)

import sys
with avb.open(sys.argv[1]) as bin_file:
	
	model_binview.setBinViewInfo(
		binviewitemtypes.BSBinViewInfo.from_binview(bin_file.content.view_setting)
	)
	
#	wnd_siftwidget.setSiftOptions([
#		avbutils.bins.BinSiftOption.from_sift_item(s) for s in bin_file.content.sifted_settings
#	])

wnd_siftwidget.resetAllCriteria()

my_criteria = [
	[
		sifters.BSAnyColumnSifter(),
		sifters.BSRangeSifter(data_role=binitemtypes.BSBinItemDataRoles.TimecodeRangeRole),
		sifters.BSAnyColumnSifter(),
	],
	[
		sifters.BSNoColumnSifter(),
		sifters.BSSingleColumnSifter(sift_column_info=binviewitemtypes.BSBinViewColumnInfo(avbutils.bins.BinColumnFieldIDs.Tracks, format_id=avbutils.bins.BinColumnFormat.UserText, display_name="Tracks", is_hidden=False)),
		sifters.BSAnyColumnSifter(sift_string="Heehee")
	]
]

wnd_siftwidget.setCriteria(my_criteria)

app.exec()