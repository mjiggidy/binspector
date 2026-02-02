from PySide6 import QtCore, QtGui
import enum, typing
from ..binview import binviewmodel, binviewitems

import avbutils

class BSBinViewColumnEditorFeature(enum.Enum):
	"""Editor column features"""

	GripperColumn     = enum.auto()
	NameColumn        = enum.auto()
	DataFormatColumn  = enum.auto()
	VisibilityColumn  = enum.auto()
	DeleteColumn      = enum.auto()

class BSBinViewColumnEditorProxyModel(QtCore.QAbstractProxyModel):
	"""Proxy model for editing bin view column data"""

	DEFAULT_FLAGS = QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled

	def __init__(self):

		super().__init__()

		self._editor_columns:list[BSBinViewColumnEditorFeature] = [
			BSBinViewColumnEditorFeature.NameColumn,
			BSBinViewColumnEditorFeature.DataFormatColumn,
			BSBinViewColumnEditorFeature.DeleteColumn,
			BSBinViewColumnEditorFeature.VisibilityColumn,
		]

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model to edit (just an alias for `setSourceModel()`)"""

		self.setSourceModel(bin_view_model)
		self.sourceModel().dataChanged.connect(self.sourceDataChanged)

	def features(self) -> list[BSBinViewColumnEditorFeature]:

		return list(self._editor_columns)

	def featureForColumn(self, column:int) -> BSBinViewColumnEditorFeature:
		"""Return the editor feature for a given logical column"""

		return self._editor_columns[column]
	
	def featureForIndex(self, index:QtCore.QModelIndex) -> BSBinViewColumnEditorFeature:
		"""Determine editor column feature for a given index"""

		return self.featureForColumn(index.column())
	
	def binViewColumnForIndex(self, index:QtCore.QModelIndex) -> binviewitems.BSBinViewColumnInfo:
		"""Get the `BSBinViewColumnInfo` for a given index"""

		if not index.isValid():
			return None
		
		return self.sourceModel().data(binviewitems.BSBinColumnInfoRole.RawColumnInfo)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		feature = self.featureForIndex(proxyIndex)

		source_index =  self.mapToSource(proxyIndex)
		
		if feature == BSBinViewColumnEditorFeature.NameColumn:

			return source_index.data(role)

		elif feature == BSBinViewColumnEditorFeature.VisibilityColumn and role == QtCore.Qt.ItemDataRole.DecorationRole:

			is_hidden =source_index.data(binviewitems.BSBinColumnInfoRole.IsHiddenRole)
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.UserOffline) if is_hidden else QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderDragAccept)

		elif feature == BSBinViewColumnEditorFeature.DataFormatColumn and role == QtCore.Qt.ItemDataRole.DisplayRole:

			return str(source_index.data(binviewitems.BSBinColumnInfoRole.FormatIdRole))[0]
		
		elif feature == BSBinViewColumnEditorFeature.DeleteColumn and role == QtCore.Qt.ItemDataRole.DecorationRole:

			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove)
		
	def setData(self, index:QtCore.QModelIndex, value:typing.Any, /, role:QtCore.Qt.ItemDataRole):

		if not super().setData(index, value, role):
			return False
		
		index_start = index.siblingAtColumn(0)
		index_end = index.siblingAtColumn(self.columnCount(index.parent())-1)

		self.dataChanged.emit(index_start, index_end)
		return True
	
	def updateRowForIndex(self, index:QtCore.QModelIndex):
		"""Emit `dataChanged` for the entire row"""

		index_start = index.siblingAtColumn(0)
		index_end   = index.siblingAtColumn(self.columnCount(index.parent())-1)

		self.dataChanged.emit(index_start, index_end)
		print("HEEE")

	@QtCore.Slot(object, object, object)
	def sourceDataChanged(self, source_index_start:QtCore.QModelIndex, source_index_end:QtCore.QModelIndex, roles:list):

		# NOTE: Haven't needed/tested this yet.  Maybe just rewrite instead of making this work because you know.
		# But I'm guessing when the sourceModel is changed via other means, I'll need to intercept its dataChanged
		# map the proxy and re-emit)

		# Map source index to proxy and get new first/last order based on row
		proxy_first_row, proxy_last_row = sorted(self.mapFromSource(source_index_start).row(), self.mapFromSource(source_index_end).row())

		for proxy_row in range(proxy_first_row, proxy_last_row+1):
			self.updateRowForIndex(self.index(proxy_first_row, 0, QtCore.QModelIndex()))
			print("Update proxy row", proxy_row)

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
		flags = self.sourceModel().flags(source_index) if source_index.isValid() else self.DEFAULT_FLAGS

		flags |= QtCore.Qt.ItemFlag.ItemIsDropEnabled | QtCore.Qt.ItemFlag.ItemIsDragEnabled
		
		if editor_feature == BSBinViewColumnEditorFeature.NameColumn and index.data(binviewitems.BSBinColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User:
			flags |= QtCore.Qt.ItemFlag.ItemIsEditable
			
		return flags
	
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		# NOTE: 02 Feb 2026 11:0am: This is officially the dumbest I've been yet.
		# Took me like two weeks to figure out THIS WAS ALL I EVER NEEDED TO DO.

		return self.index(sourceIndex.row(), sourceIndex.column(), sourceIndex.parent())
	
	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if not proxyIndex.isValid():
			return QtCore.QModelIndex()

		return self.sourceModel().index(proxyIndex.row(), proxyIndex.column(), QtCore.QModelIndex())