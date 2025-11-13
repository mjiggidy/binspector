import avb, avbutils
from PySide6 import QtCore, QtWidgets
from binspector.widgets import siftwidget

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd = siftwidget.BSSiftSettingsWidget()

font = wnd.font()
font.setPointSizeF(font.pointSizeF() * 0.8)

wnd.setWindowTitle("Custom Sift")
wnd.setFont(font)
wnd.setWindowFlag(QtCore.Qt.WindowType.Tool)
wnd.show()

geo = wnd.geometry()
geo.setWidth(geo.height() * 1.75)

wnd.setGeometry(geo)
wnd.setFixedHeight(geo.height())

wnd.btn_dialog.accepted.connect(app.quit)
wnd.btn_dialog.rejected.connect(app.quit)
wnd.btn_dialog.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).clicked.connect(lambda: print(wnd.siftOptions()))

import sys
with avb.open(sys.argv[1]) as bin_file:
	bin_view = bin_file.content.view_setting
	wnd.setBinView(bin_view)

options = []

options.append(siftwidget.BSSiftOption(
	sift_method=avbutils.bins.BinSiftMethod.MATCHES_EXACTLY,
	sift_text="Poopy",
	sift_column="Name",
))

wnd.setSiftOptions(options)

app.exec()