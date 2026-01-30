from PySide6 import QtCore, QtGui
import enum
from ..binview import binviewmodel, binviewitems

class BSBinViewColumnEditorFeature(enum.Enum):
	"""Editor column features"""

	GripperColumn     = enum.auto()
	NameColumn        = enum.auto()
	DataFormatColumn  = enum.auto()
	VisibilityColumn  = enum.auto()
	DeleteColumn      = enum.auto()

class BSBinViewColumnEditorProxyModel(QtCore.QAbstractProxyModel):
	"""Proxy model for editing bin view column data"""

	def __init__(self):

		super().__init__()

		self._editor_columns:list[BSBinViewColumnEditorFeature] = [
			BSBinViewColumnEditorFeature.NameColumn,
			BSBinViewColumnEditorFeature.DataFormatColumn,
			BSBinViewColumnEditorFeature.DeleteColumn,
			BSBinViewColumnEditorFeature.VisibilityColumn,
		]

		self.modelReset.connect(print)

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model to edit (just an alias for `setSourceModel()`)"""

		self.setSourceModel(bin_view_model)

	
	def featureForIndex(self, index:QtCore.QModelIndex) -> BSBinViewColumnEditorFeature|None:
		"""Determine editor column feature for a given index"""
		
		if not index.isValid():
			return None

		return self._editor_columns[index.column()]
	
	def binViewColumnForIndex(self, index:QtCore.QModelIndex) -> binviewitems.BSBinViewColumnInfo:
		"""Get the `BSBinViewColumnInfo` for a given index"""

		if not index.isValid():
			return None
		
		return self.sourceModel().data(binviewitems.BSBinColumnInfoRole.RawColumnInfo)
	
#	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
#		
#		feature = self.featureForIndex(proxyIndex)
#		
#		if feature == BSBinViewColumnEditorFeature.NameColumn:
#			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(role)
#
#		elif feature == BSBinViewColumnEditorFeature.VisibilityColumn:
#			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binviewitems.BSBinColumnInfoRole.IsHiddenRole)
#
#		elif feature == BSBinViewColumnEditorFeature.DataFormatColumn:
#			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binviewitems.BSBinColumnInfoRole.FormatIdRole)
#		
#		elif feature == BSBinViewColumnEditorFeature.DeleteColumn and role == QtCore.Qt.ItemDataRole.DecorationRole:
#			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditDelete)
	

	###
	
	def columnCount(self, /, parent:QtCore.QModelIndex):
		
		if parent.isValid():
			return 0
		
		return len(self._editor_columns)
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return 0
		
		if not self.sourceModel():
			return 0
		
		return self.sourceModel().rowCount(QtCore.QModelIndex())
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex):

		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def parent(self, index:QtCore.QModelIndex) -> QtCore.QModelIndex:

		return QtCore.QModelIndex()
	
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if not sourceIndex.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(sourceIndex.row(), self._editor_columns.index(BSBinViewColumnEditorFeature.NameColumn))
	
	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if not proxyIndex.isValid():
			return QtCore.QModelIndex()
		
		editor_feature = self.featureForIndex(proxyIndex)

		if editor_feature in (BSBinViewColumnEditorFeature.NameColumn, BSBinViewColumnEditorFeature.VisibilityColumn, BSBinViewColumnEditorFeature.DataFormatColumn):
			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex())
		
		else:
			return QtCore.QModelIndex()