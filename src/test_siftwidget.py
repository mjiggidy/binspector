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
wnd.btn_dialog.button(QtWidgets.QDialogButtonBox.StandardButton.Reset).clicked.connect(lambda: print(wnd.setSiftOptions()))

import sys
with avb.open(sys.argv[1]) as bin_file:
	bin_view = bin_file.content.view_setting
	wnd.setBinView(bin_view)
	wnd.setSiftOptions([
		siftwidget.BSSiftOption.from_sift_item(s) for s in bin_file.content.sifted_settings
	])
	print(bin_file.content.sifted)

app.exec()