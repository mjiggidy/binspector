from PySide6 import QtCore
import enum

class BSBinViewColumnEditorColumns(enum.Enum):

	GripperColumn     = enum.auto()
	NameColumn        = enum.auto()
	DataFormatColumn  = enum.auto()
	VisibilityColumn  = enum.auto()
	DeleteColumn      = enum.auto()

class BSBinViewColumnEditorProxyModel(QtCore.QIdentityProxyModel):
	"""Proxy model for editing bin view column data"""
	pass