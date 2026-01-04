import typing
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

	def getIcon(self, key:typing.Hashable) -> QtGui.QIcon:
		"""Given a key, lookup and return an existing `QIcon`, or return invalid"""

		if key not in self._icons:
			# NOTE: Returns invalid `QIcon()`
			# TODO: Generate and add icon
			return QtGui.QIcon()

		return self._icons[key]