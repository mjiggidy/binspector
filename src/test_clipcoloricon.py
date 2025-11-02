import sys
import avbutils
from os import PathLike
from PySide6 import QtCore, QtSvg, QtGui, QtWidgets
from binspector.res import icons_gui
from binspector.core.icons import BSPalettedClipColorIconEngine, BSPaletteWatcherForSomeReason

app = QtWidgets.QApplication()
app.setStyle("Fusion")

window = QtWidgets.QWidget()
window.setLayout(QtWidgets.QHBoxLayout())
window.layout().setSpacing(0)

palette_watcher = BSPaletteWatcherForSomeReason()
app.paletteChanged.connect(palette_watcher.setPalette)

for color in avbutils.get_default_clip_colors():

	chip_color  = QtGui.QColor(*color.as_rgb8())
	chip_engine = BSPalettedClipColorIconEngine(chip_color, palette_watcher)

	window.layout().addWidget(
		QtWidgets.QPushButton(
			icon=QtGui.QIcon(chip_engine))
	)

window.show()

sys.exit(app.exec())