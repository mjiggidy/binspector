import sys
import avbutils
from os import PathLike
from PySide6 import QtCore, QtSvg, QtGui, QtWidgets
from binspector.res import icons_gui
from binspector.core.icons import BSPalettedClipColorIconEngine, BSPaletteWatcherForSomeReason, BSPalettedMarkerIconEngine

app = QtWidgets.QApplication()
app.setStyle("Fusion")

window_colorchips = QtWidgets.QWidget()
window_colorchips.setLayout(QtWidgets.QHBoxLayout())
window_colorchips.layout().setSpacing(0)

palette_watcher = BSPaletteWatcherForSomeReason()
app.paletteChanged.connect(palette_watcher.setPalette)

for color in avbutils.get_default_clip_colors():

	chip_color  = QtGui.QColor(*color.as_rgb8())
	chip_engine = BSPalettedClipColorIconEngine(chip_color, palette_watcher)

	window_colorchips.layout().addWidget(
		QtWidgets.QPushButton(
			icon=QtGui.QIcon(chip_engine))
	)

window_colorchips.show()

window_markers = QtWidgets.QWidget()
window_markers.setLayout(QtWidgets.QHBoxLayout())
window_markers.layout().setSpacing(0)

for marker_color in avbutils.MarkerColors:

	marker_engine = BSPalettedMarkerIconEngine(
		QtGui.QColor(marker_color.value),
		palette_watcher
	)

	window_markers.layout().addWidget(
		QtWidgets.QPushButton(
			icon=QtGui.QIcon(marker_engine)
		)
	)

window_markers.layout().addWidget(
	QtWidgets.QPushButton(
		icon=QtGui.QIcon(BSPalettedMarkerIconEngine(
			QtGui.QColor(),
			palette_watcher
		))
	)
)

window_markers.show()


BIN_ITEM_ICONS = {
	avbutils.BinDisplayItemTypes.MASTER_CLIP: "/home/mjordan/dev/binspector/graphics/binitems/item_masterclip_v01_themed.svg",
	avbutils.BinDisplayItemTypes.SEQUENCE:    "/home/mjordan/dev/binspector/graphics/binitems/item_sequence_v01_themed.svg",
	avbutils.BinDisplayItemTypes.GROUP:    "/home/mjordan/dev/binspector/graphics/binitems/item_groupclip_v01_themed.svg",
}

window_binitems = QtWidgets.QWidget()
window_binitems.setLayout(QtWidgets.QVBoxLayout())
window_binitems.setWindowTitle("Bin Items")

for bin_item in avbutils.BinDisplayItemTypes:

	btn = QtWidgets.QPushButton()
	btn.setToolTip(bin_item.name)
	btn.setIconSize(QtCore.QSize(16,9) * 2)
	if bin_item in BIN_ITEM_ICONS:
		btn.setIcon(QtGui.QIcon(BIN_ITEM_ICONS[bin_item]))

	window_binitems.layout().addWidget(btn)

window_binitems.show()

sys.exit(app.exec())