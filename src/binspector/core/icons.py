import weakref, logging, typing
from os import PathLike
from PySide6 import QtCore, QtGui, QtSvg
from ..utils import drawing

class BSPaletteWatcherForSomeReason(QtCore.QObject):
	"""Watch for palette changes ugh"""

	sig_palette_changed = QtCore.Signal(QtGui.QPalette)
	"""Oh look the palette changed"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._icon_engines:set[weakref.ReferenceType["BSPalettedSvgIconEngine"]] = set()

	def addIconEngine(self, paletted_engine:"BSPalettedSvgIconEngine"):
		self._icon_engines.add(weakref.ref(paletted_engine))
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

		for icon_engine in self._icon_engines:

			if not icon_engine():

				logging.getLogger(__name__).debug("Discarding stale weakref: %s", icon_engine)
				self._icon_engines.discard(icon_engine)

			else:
				icon_engine().setPalette(palette)

		self.sig_palette_changed.emit(palette)

class BSIconProvider:
	"""Provide icons based on lookup"""

	def __init__(self):

		self._icons:dict[typing.Hashable, QtGui.QIcon] = dict()
	
	def icons(self) -> list[QtGui.QIcon]:
		return self._icons
	
	def addIcon(self, key:typing.Hashable, icon:QtGui.QIcon):
		self._icons[key] = icon

	def getIcon(self, key:typing.Hashable) -> QtGui.QIcon:

		if key not in self._icons:
			# TODO: Generate and add icon
			return QtGui.QIcon()
		
		return self._icons[key]
	
class BSAbstractPalettedIconEngine(QtGui.QIconEngine):

	def __init__(self, palette_watcher:BSPaletteWatcherForSomeReason, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._palette = QtGui.QPalette()
		self._cache:dict[int,QtGui.QPixmap] = dict()
		
		self._palette_watcher = palette_watcher
		self._palette_watcher.addIconEngine(self)

	def setPalette(self, palette:QtGui.QPalette):
		self._palette = palette
	
	def palette(self) -> QtGui.QPalette:
		return self._palette
	
	def _makeHash(self, size:QtCore.QSize, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State) -> int:
		""""""

		return hash((
			size,
			mode,
			state,
			self._palette.cacheKey()
		))
	
class BSPalettedClipColorIconEngine(BSAbstractPalettedIconEngine):

	def __init__(self, clip_color:QtGui.QColor, palette_watcher:BSPaletteWatcherForSomeReason, *args, border_width:int=2, **kwargs):

		super().__init__(palette_watcher, *args, **kwargs)

		self._clip_color   = clip_color
		self._border_width = border_width

	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):

		drawing.draw_clip_color_chip(
			painter      = painter,
			canvas       = rect,
			clip_color   = self._clip_color,
			border_width = self._border_width,
			border_color = self._palette.windowText().color(),
			shadow_color = self._palette.shadow().color(),
		)

	def clone(self) -> "BSPalettedClipColorIconEngine":
		
		logging.getLogger(__name__).debug("I do be clonin haha look")
		return self.__class__(self._clip_color, self._palette_watcher)
	
	def addPixmap(self, pixmap:QtGui.QPixmap, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):

		h = self._makeHash(pixmap.size(), mode, state)
		self._cache[h] = pixmap
	
	def pixmap(self, size, mode, state):

		# Pull from cache?
		h = self._makeHash(size, mode, state)
		if h in self._cache:
			return self._cache[h]
		
		# Or draw new one
		logging.getLogger(__name__).debug("Drawing new icon for size=%s, mode=%s, state=%s (hash=%s)", size, mode, state, h)
		pixmap = QtGui.QPixmap(size)
		pixmap.fill(QtCore.Qt.GlobalColor.transparent)
		
		self.paint(QtGui.QPainter(pixmap), pixmap.rect(), mode, state)
		self._cache[h] = pixmap
		return pixmap

class BSPalettedSvgIconEngine(BSAbstractPalettedIconEngine):
	
	def __init__(self, svg_path:PathLike, palette_watcher:BSPaletteWatcherForSomeReason, *args, **kwargs):

		super().__init__(palette_watcher, *args, **kwargs)

		self._svg_path     = svg_path

		self._renderer     = QtSvg.QSvgRenderer()
		self._palette_dict = self._paletteToDict(self._palette)
		self._svg_template = bytes(QtCore.QResource(svg_path).uncompressedData().data()).decode("utf-8")
	
	def clone(self) -> "BSPalettedSvgIconEngine":
		logging.getLogger(__name__).debug("I do be clonin haha look")
		return self.__class__(self._svg_path, self._palette_watcher)
	
	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):
		
		# Replace SVG color strings with QPalette color roll names, then render
		self._renderer.load(self._svg_template.format_map(self._palette_dict).encode("utf-8"))
		self._renderer.render(painter)

		self.addPixmap(painter.device(), mode, state)
	
	def pixmap(self, size, mode, state):

		# Pull from cache?
		h = self._makeHash(size, mode, state)
		if h in self._cache:
			return self._cache[h]
		
		# Or draw new one
		pixmap = QtGui.QPixmap(size)
		pixmap.fill(QtCore.Qt.GlobalColor.transparent)
		self.paint(QtGui.QPainter(pixmap), pixmap.rect(), mode, state)

		return pixmap
	
	def setPalette(self, palette:QtGui.QPalette):

		super().setPalette(palette)
		self._palette_dict = self._paletteToDict(palette)

	@staticmethod
	def _paletteToDict(palette:QtGui.QPalette) -> dict[str,str]:

		# NOTE: NColorRoles causes a periodic segfault that was JUST RUINING MY LIFE for a long time there
		# Paraphrasing QPalette docs: "color role int should be less than NColorRoles" so I guess it's more of a sentinel
		return {role.name: palette.color(role).name() for role in QtGui.QPalette.ColorRole if role.name != "NColorRoles"}