import sys
from os import PathLike
from PySide6 import QtCore, QtSvg, QtGui, QtWidgets
from binspector.res import icons_gui

class BSPalettedSvgIconEngine(QtGui.QIconEngine):
	
	def __init__(self, svg_path:PathLike, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._svg_path     = svg_path
		self._renderer     = QtSvg.QSvgRenderer()
		self._palette      = QtGui.QPalette()
		self._palette_dict = self._paletteToDict(self._palette)
		self._svg_template = QtCore.QByteArray(
			bytes(QtCore.QResource(svg_path).data())
		).toStdString()

		self._cache:dict[int,QtGui.QPixmap] = dict()
	
	def clone(self) -> "BSPalettedSvgIconEngine":
		return self.__class__(self._svg_path)
	
	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):

		print("New render")
		
		self._renderer.load(self._svg_template.format_map(self._palette_dict).encode("utf-8"))
		self._renderer.render(painter)

		self.addPixmap(painter.device(), mode, state, str(self._palette_dict))

	def addPixmap(self, pixmap:QtGui.QPixmap, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State, palette:QtGui.QPalette):

		h = hash((pixmap.size(), mode, state, palette))
		self._cache[h] = pixmap
		print("added as ", h)
	
	def pixmap(self, size, mode, state):

		h = hash((size, mode, state, str(self._palette_dict)))
		if h in self._cache:
			print("Return cache")
			return self._cache[h]
		
		pixmap = QtGui.QPixmap(size)
		pixmap.fill(QtCore.Qt.GlobalColor.transparent)
		self.paint(QtGui.QPainter(pixmap), pixmap.rect(), mode, state)

		return pixmap
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

		self._palette      = palette
		self._palette_dict = self._paletteToDict(palette)

	@staticmethod
	def _paletteToDict(palette:QtGui.QPalette) -> dict[str,str]:
		return {role.name: palette.color(role).name() for role in QtGui.QPalette.ColorRole}
	


ICON_RESOURCES = ["list","frame","script"]

app = QtWidgets.QApplication()
app.setStyle("Fusion")

window = QtWidgets.QWidget()
window.setLayout(QtWidgets.QHBoxLayout())
window.layout().setSpacing(0)

for mode in ICON_RESOURCES:

	icon_engine = BSPalettedSvgIconEngine(f":/icons/gui/view_{mode}.svg")
	icon = QtGui.QIcon(icon_engine)

	button = QtWidgets.QPushButton()
	button.setIconSize(QtCore.QSize(16,16))
	button.setIcon(icon)

	app.paletteChanged.connect(icon_engine.setPalette)

	window.layout().addWidget(button)

window.show()

sys.exit(app.exec())