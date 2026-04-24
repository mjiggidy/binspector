import enum

class BSBinWidgetFeatures(enum.Flag):
	"""Scroll bar widget featuers supported by `binwidget`"""

	ShowAllItems              = enum.auto()
	"""Toggle all items (rows) visible"""

	LIST_ShowAllColumns       = enum.auto()
	"""Toggle all columns visible"""

	LIST_StatsView            = enum.auto()
	"""Toggle row/column count stats view"""

	FRAME_StatsView           = enum.auto()
	"""Toglge item count stats view"""

	FRAME_SnapToGrid          = enum.auto()
	"""Toggle grid and snap-to-grid behavior"""

	FRAME_Ruler               = enum.auto()
	"""Toggle ruler"""

	FRAME_Map                 = enum.auto()
	"""Toggle bin map"""

	AllFeatures = ShowAllItems | LIST_ShowAllColumns | LIST_StatsView | FRAME_StatsView | FRAME_SnapToGrid | FRAME_Ruler | FRAME_Map
	"""All features selected"""