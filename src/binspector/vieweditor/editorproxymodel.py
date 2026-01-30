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

		
		#self.modelReset.connect(print)

		self._default_flags = QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model to edit (just an alias for `setSourceModel()`)"""

		self.setSourceModel(bin_view_model)

	def features(self) -> list[BSBinViewColumnEditorFeature]:

		return list(self._editor_columns)

	def featureForColumn(self, column:int) -> BSBinViewColumnEditorFeature|None:
		"""Return the editor feature for a given logical column"""

		return self._editor_columns[column]
	
	def featureForIndex(self, index:QtCore.QModelIndex) -> BSBinViewColumnEditorFeature|None:
		"""Determine editor column feature for a given index"""
		
		if not index.isValid():
			return None

		return self.featureForColumn(index.column())
	
	def binViewColumnForIndex(self, index:QtCore.QModelIndex) -> binviewitems.BSBinViewColumnInfo:
		"""Get the `BSBinViewColumnInfo` for a given index"""

		if not index.isValid():
			return None
		
		return self.sourceModel().data(binviewitems.BSBinColumnInfoRole.RawColumnInfo)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		feature = self.featureForIndex(proxyIndex)
		
		if feature == BSBinViewColumnEditorFeature.NameColumn:
			return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(role)

		elif feature == BSBinViewColumnEditorFeature.VisibilityColumn and role == QtCore.Qt.ItemDataRole.DecorationRole:
			is_hidden = self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binviewitems.BSBinColumnInfoRole.IsHiddenRole)
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.UserOffline) if is_hidden else QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderDragAccept)

		elif feature == BSBinViewColumnEditorFeature.DataFormatColumn and role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binviewitems.BSBinColumnInfoRole.FormatIdRole))[0]
		
		elif feature == BSBinViewColumnEditorFeature.DeleteColumn and role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove)
	

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
	
	def flags(self, index:QtCore.QModelIndex):
		
		source_index    = self.mapToSource(index)
		editor_feature  = self.featureForIndex(index)

		# Start With Base Flags
		
		flags = self.sourceModel().flags(source_index) if source_index.isValid() else self._default_flags

		flags |= QtCore.Qt.ItemFlag.ItemIsDropEnabled | QtCore.Qt.ItemFlag.ItemIsDragEnabled
		import avbutils
		if editor_feature == BSBinViewColumnEditorFeature.NameColumn and index.data(binviewitems.BSBinColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User:
			flags |= QtCore.Qt.ItemFlag.ItemIsEditable
			
		return flags
	
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