import sys
from os import PathLike
from PySide6 import QtCore, QtSvg, QtGui, QtWidgets
from binspector.res import icons_gui
from binspector.core.icons import BSPalettedIcon, BSPalettedSvgIconEngine
	


ICON_RESOURCES = ["list","frame","script"]

app = QtWidgets.QApplication()
app.setStyle("Fusion")

window = QtWidgets.QWidget()
window.setLayout(QtWidgets.QHBoxLayout())
window.layout().setSpacing(0)

for mode in ICON_RESOURCES:

	icon_engine = BSPalettedSvgIconEngine(f":/icons/gui/view_{mode}.svg")
	icon = BSPalettedIcon(icon_engine)

	button = QtWidgets.QPushButton()
	button.setIconSize(QtCore.QSize(16,16))
	button.setIcon(icon)

	app.paletteChanged.connect(icon.engine().setPalette)

	window.layout().addWidget(button)

window.show()

sys.exit(app.exec())