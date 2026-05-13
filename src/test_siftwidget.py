import avb, avbutils
from PySide6 import QtCore, QtWidgets
from binspector.siftwidget import scopesmodel, siftwidget
from binspector.textview import bincompositemodel
from binspector.binview import binviewmodel, binviewitemtypes
from binspector.binfilters import binviewproxymodel
from binspector.binfilters.siftfilter import sifters, siftproxymodel
from binspector.binitems import binitemtypes, binitemsmodel

app = QtWidgets.QApplication()
app.setStyle("Fusion")

model_binview       = binviewmodel.BSBinViewModel()
model_binviewfilter = binviewproxymodel.BSBinViewFilterProxyModel(bin_columns_model=model_binview)
model_binitems      = binitemsmodel.BSBinItemModel()
model_composite     = bincompositemodel.BSBinCompositeModel(item_model=model_binitems, view_model=model_binviewfilter)
model_siftfilter    = siftproxymodel.BSBinSiftFilterProxyModel()
model_siftfilter.setSourceModel(model_composite)

# Just a temp bin viewer
wnd_binviewer = QtWidgets.QTreeView()
wnd_binviewer.setModel(model_siftfilter)
wnd_binviewer.show()

# Sift Widget
wnd_siftwidget = siftwidget.BSSiftSettingsWidget()
wnd_siftwidget.setSiftFilterModel(model_siftfilter)
wnd_siftwidget.setWindowTitle("Custom Sift")
wnd_siftwidget.setWindowFlag(QtCore.Qt.WindowType.Tool)
wnd_siftwidget.show()
geo = wnd_siftwidget.geometry()
geo.setWidth(geo.height() * 1.75)
wnd_siftwidget.setGeometry(geo)
wnd_siftwidget.setFixedHeight(geo.height())




import sys
with avb.open(sys.argv[1]) as bin_file:
	
	model_binview.setBinViewInfo(
		binviewitemtypes.BSBinViewInfo.from_binview(bin_file.content.view_setting)
	)

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