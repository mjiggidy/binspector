import sys
from PySide6 import QtCore, QtSvg, QtSvgWidgets, QtGui, QtWidgets
from binspector.res import icons_gui

def palette_to_dict(palette:QtGui.QPalette) -> dict[str, QtGui.QColor]:
	"""Pack roles and their hex values to a dict for string replacement"""

	roles = {role.name: palette.color(role).name() for role in QtGui.QPalette.ColorRole}
	#print(roles)
	return roles


def replace_color(svg_path, replacements:dict|None=None) -> str:
	"""Replace templated ColorRoles in an SVG with the provided palette colors"""

	svg_data = QtCore.QResource(svg_path).data()
	svg_string = bytes(svg_data).decode("utf-8").format_map(replacements)
	#print(svg_string)
	return QtCore.QByteArray(svg_string)


ICON_RESOURCE_PATH = ":/icons/gui/view_list.svg"

app = QtWidgets.QApplication()

svg_palette   = palette_to_dict(app.palette())
svg_processed = replace_color(ICON_RESOURCE_PATH, svg_palette)

#QtSvg.QSvgGenerator()

window = QtSvgWidgets.QSvgWidget()
window.load(svg_processed)

app.paletteChanged.connect(lambda pal:
	window.load(
		replace_color(ICON_RESOURCE_PATH, palette_to_dict(pal))
	)
)

window.setFixedSize(QtCore.QSize(64,64))
window.show()

sys.exit(app.exec())