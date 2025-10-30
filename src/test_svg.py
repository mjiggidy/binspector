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
		self._cache:dict[int,QtGui.QPixmap] = dict()
		self._palette_dict = self._paletteToDict(self._palette)
		
		self._svg_template = QtCore.QByteArray(
			bytes(QtCore.QResource(svg_path).data())
		).toStdString()

	
	def clone(self) -> "BSPalettedSvgIconEngine":
		return self.__class__(self._svg_path)
	
	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):
		
		self._renderer.load(self._svg_template.format_map(self._palette_dict).encode("utf-8"))
		self._renderer.render(painter)

		self.addPixmap(painter.device(), mode, state, str(self._palette_dict))

	def addPixmap(self, pixmap:QtGui.QPixmap, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State, palette:QtGui.QPalette):

		h = self._makeHash(pixmap.size(), mode, state, palette)
		self._cache[h] = pixmap
	
	def pixmap(self, size, mode, state):

		# Pull from cache?
		h = self._makeHash(size, mode, state, str(self._palette_dict))
		if h in self._cache:
			return self._cache[h]
		
		# Or draw new one
		pixmap = QtGui.QPixmap(size)
		pixmap.fill(QtCore.Qt.GlobalColor.transparent)
		self.paint(QtGui.QPainter(pixmap), pixmap.rect(), mode, state)

		return pixmap
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

		self._palette      = palette
		self._palette_dict = self._paletteToDict(palette)
	
	def palette(self) -> QtGui.QPalette:
		return self._palette

	@staticmethod
	def _paletteToDict(palette:QtGui.QPalette) -> dict[str,str]:
		return {role.name: palette.color(role).name() for role in QtGui.QPalette.ColorRole}
	
	@staticmethod
	def _makeHash(size:QtCore.QSize, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State, palette_dict:dict[str,str]):

		return hash((size, mode, state, palette_dict))

class BSPalettedIcon(QtGui.QIcon):
	"""A QIcon with support for paletted SVG icons via `BSPaletttedSvgIconEngine`"""

	def __init__(self, icon_engine:BSPalettedSvgIconEngine, *args, **kwargs):

		super().__init__(icon_engine, *args, **kwargs)
		self._engine = icon_engine

	def engine(self) -> QtGui.QIconEngine:
		return self._engine
	
	# NOTE: Tried a `setPalette() self._engine.setPalette(palette)` here.
	# Didn't... quite work? It was weird.  So, connect to icon.engine().setPalette instead
	# Bruh I dunno

	def palette(self) -> QtGui.QPalette:
		return self._engine.palette()
	


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