from PySide6 import QtCore, QtWidgets

class BSListViewConfig:

	DEFAULT_ITEM_PADDING:QtCore.QMargins = QtCore.QMargins(16,4,16,4)
	"""Default padding inside view item"""

	DEFAULT_SELECTION_BEHAVIOR = QtWidgets.QTreeView.SelectionBehavior.SelectRows
	"""Default selection behavior (select rows, columns, or items)"""

	DEFAULT_SELECTION_MODE     = QtWidgets.QTreeView.SelectionMode    .ExtendedSelection
	"""Default selection mode (continuous, extended, etc)"""

	ALLOW_KEEP_CURRENT_SELECTION_BETWEEN_MODES = False
	"""Maintain selected items when changing between selection modes (rows/colums/items)"""
	# NOTE: There's a bool at work in the logic as well -- both'll need to be True

	# NOT USED? =====
	SELECTION_BEHAVIOR_MODIFIER_KEY:QtCore.Qt.KeyboardModifier = QtCore.Qt.KeyboardModifier.AltModifier # NOT USED?
	BINVIEW_COLUMN_WIDTH_ADJUST:int = 64	# NOT USED?
	"""Adjust binview-specified column widths for better fit"""

class BSFrameViewConfig:
	"""Bin Frame View Mode Config"""

	GRID_UNIT_SIZE     = QtCore.QSizeF(18,12) # 18x12 in scene units
	"""Unit size in scene coordinates"""

	GRID_DIVISIONS     = QtCore.QPoint(3,3)   # 3 ticks along X and Y
	"""Divisions per grid unit"""

	DEFAULT_ITEM_FLAGS = \
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable|\
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|\
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
	"""Default item flags"""