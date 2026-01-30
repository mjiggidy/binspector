from PySide6 import QtCore, QtGui
import enum
from . import binviewmodel

class BSBinViewColumnEditorColumns(enum.Enum):

	GripperColumn     = enum.auto()
	NameColumn        = enum.auto()
	DataFormatColumn  = enum.auto()
	VisibilityColumn  = enum.auto()
	DeleteColumn      = enum.auto()

class BSBinViewColumnEditorProxyModel(QtCore.QIdentityProxyModel):
	"""Proxy model for editing bin view column data"""

	def __init__(self):

		super().__init__()

		self._editor_columns:list[BSBinViewColumnEditorColumns] = [
			BSBinViewColumnEditorColumns.NameColumn,
			BSBinViewColumnEditorColumns.DataFormatColumn,
			BSBinViewColumnEditorColumns.DeleteColumn,
			BSBinViewColumnEditorColumns.VisibilityColumn,
		]
	
	def columnCount(self, /, parent:QtCore.QModelIndex):
		
		if parent.isValid():
			return 0
		
		return len(self._editor_columns)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		editor_role = self._editor_columns[proxyIndex.column()]
		
		if editor_role == BSBinViewColumnEditorColumns.NameColumn:
			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(role)
		elif editor_role == BSBinViewColumnEditorColumns.VisibilityColumn:
			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binviewmodel.BSBinColumnInfoRole.IsHiddenRole)
		elif editor_role == BSBinViewColumnEditorColumns.DataFormatColumn:
			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binviewmodel.BSBinColumnInfoRole.FormatIdRole)
		
		elif editor_role == BSBinViewColumnEditorColumns.DeleteColumn and role == QtCore.Qt.ItemDataRole.DecorationRole:

			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditDelete)
		
	def headerRoleForIndex(self, index:QtCore.QModelIndex) -> BSBinViewColumnEditorColumns:

		return self._editor_columns[index.column()]