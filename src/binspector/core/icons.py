import weakref, logging
from os import PathLike
from PySide6 import QtCore, QtGui, QtSvg

class BSPaletteWatcherForSomeReason(QtCore.QObject):
	"""Watch for palette changes ugh"""

	sig_palette_changed = QtCore.Signal(QtGui.QPalette)
	"""Oh look the palette changed"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._icon_engines:set[weakref.ReferenceType["BSPalettedSvgIconEngine"]] = set()

	def addIconEngine(self, paletted_engine:"BSPalettedSvgIconEngine"):
		self._icon_engines.add( weakref.ref(paletted_engine))
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

		for icon_engine in self._icon_engines:

			if not icon_engine():

				logging.getLogger(__name__).debug("Discarding stale weakref: %s", icon_engine)
				self._icon_engines.discard(icon_engine)

			else:
				icon_engine().setPalette(palette)

		self.sig_palette_changed.emit(palette)

class BSPalettedSvgIconEngine(QtGui.QIconEngine):
	
	def __init__(self, svg_path:PathLike, palette_watcher:BSPaletteWatcherForSomeReason, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._svg_path     = svg_path
		self._palette_watcher = palette_watcher

		self._renderer     = QtSvg.QSvgRenderer()
		self._palette      = QtGui.QPalette()
		self._cache:dict[int,QtGui.QPixmap] = dict()
		self._palette_dict = self._paletteToDict(self._palette)
		self._svg_template = bytes(QtCore.QResource(svg_path).uncompressedData().data()).decode("utf-8")

		self._palette_watcher.addIconEngine(self)

	
	def clone(self) -> "BSPalettedSvgIconEngine":
		logging.getLogger(__name__).debug("I do be clonin haha look")
		return self.__class__(self._svg_path, self._palette_watcher)
	
	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):
		
		# Replace SVG color strings with QPalette color roll names, then render
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
	
	def setPalette(self, palette:QtGui.QPalette):

		self._palette      = palette
		self._palette_dict = self._paletteToDict(palette)
	
	def palette(self) -> QtGui.QPalette:
		return self._palette

	@staticmethod
	def _paletteToDict(palette:QtGui.QPalette) -> dict[str,str]:

		# NOTE: NColorRoles causes a periodic segfault that was JUST RUINING MY LIFE for a long time there
		# Paraphrasing QPalette docs: "color role int should be less than NColorRoles" so I guess it's more of a sentinel
		return {role.name: palette.color(role).name() for role in QtGui.QPalette.ColorRole if role.name != "NColorRoles"}
	
	@staticmethod
	def _makeHash(size:QtCore.QSize, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State, palette_dict:dict[str,str]):

		return hash((size, mode, state, palette_dict))