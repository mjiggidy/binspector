import typing, logging
from . import icon_engines

from PySide6 import QtGui

PROPERTY_ICON_PALETTED = "icon_paletted"
"""Custom Property Key containing a resource path to a paletted SVG"""

def getPalettedIconEngine(action:QtGui.QAction) -> icon_engines.BSAbstractPalettedIconEngine|None:
	"""A QAction could have a path to a paletted SVG set as a custom propery: `PROPERTY_ICON_PALETTED`"""

	path_icon = action.property(PROPERTY_ICON_PALETTED)
	return icon_engines.BSPalettedSvgIconEngine(path_icon) if path_icon else None


class BSIconProvider:
	"""Provide `QIcon` handles based on key lookup"""

	# NOTE: Basically a cache for related QIconEngines
	# For example: One IconProvider handles all "clip type" icons in a treeview
	# Another would handle all view mode icons for a main window.  That kinda thing.

	def __init__(self):

		self._icons:dict[typing.Hashable, QtGui.QIcon] = dict()
		"""QIcon per key"""

	def icons(self) -> dict[typing.Hashable, QtGui.QIcon]:
		return self._icons

	def addIcon(self, key:typing.Hashable, icon:QtGui.QIcon):
		"""Add a `QIcon` for a key"""
		self._icons[key] = icon

	# NOTE: Plan to override this is subclasses I think
	def getIcon(self, key:typing.Hashable) -> QtGui.QIcon:
		"""Given a key, lookup and return an existing `QIcon`, or return invalid"""

		if key not in self._icons:
			# NOTE: Returns invalid `QIcon()`
			# TODO: Generate and add icon
			return QtGui.QIcon()

		return self._icons[key]
	
class BSPalettedClipColorIconProvider(BSIconProvider):

	def getIcon(self, clip_color:QtGui.QColor, border_width:int=1):

		#print("*** LOOOKING FOR ", clip_color)

		clip_color_hash = hash(clip_color.toTuple() if clip_color.isValid() else -1)

		if not clip_color_hash in self._icons:

			#print("*** LOOOKING FOR ", clip_color)

			self._icons[clip_color_hash] = icon_engines.BSPalettedClipColorIconEngine(
				clip_color=clip_color,
				border_width=border_width
			)
			logging.getLogger(__name__).debug("%s created icon %s", repr(self), repr(self._icons[clip_color_hash]))

		return super().getIcon(clip_color_hash)