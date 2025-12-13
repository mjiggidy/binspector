from PySide6 import QtCore

class BSFrameViewConfig:
	"""Bin Frame View Mode Config"""

	GRID_UNIT_SIZE     = QtCore.QSizeF(18,12) # 18x12 in scene units
	"""Unit size in scene coordinates"""

	GRID_DIVISIONS     = QtCore.QPoint(3,3)   # 3 ticks along X and Y
	"""Divisions per grid unit"""