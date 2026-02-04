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
			BSBinViewColumnEditorFeature.DeleteColumn,
			BSBinViewColumnEditorFeature.DataFormatColumn,
			BSBinViewColumnEditorFeature.VisibilityColumn,
		]

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model to edit (just an alias for `setSourceModel()`)"""

		self.setSourceModel(bin_view_model)

		self.sourceModel().rowsAboutToBeRemoved.connect(self.sourceModelAboutToRemoveRows)
		self.sourceModel().rowsRemoved.connect(self.sourceModelRowsRemoved)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelAboutToRemoveRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if self.mapFromSource(parent).isValid():
			return
		
		# NOTE: Big ol' caveat here that I'm just gonna pretend won't be a terrible problem in the future:
		# I'm trusting that row numbers remain contiguous between the source and proxy so I can still say "start at 
		# row 5 and delete the next 5" without worrying about there being any breaks in the run between the source  
		# and proxy due to different proxy row mappings.
		# I've been writing code since 1990 but I think I'm still a terrible programmer probably.
		# 12 year old kids on YouTube do it better than me
		# I'm too old to change
		# What do I do
		
		self.beginRemoveRows(QtCore.QModelIndex(), row_start, row_end)
		print("I begin")
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelRowsRemoved(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if self.mapFromSource(parent).isValid():
			return
		
		self.endRemoveRows()
		print("I end")

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
	
	def binColumnIsHiddenForIndex(self, index:QtCore.QModelIndex) -> bool:
		return self.data(index, binviewitems.BSBinColumnInfoRole.IsHiddenRole)

	def setBinColumnHiddenForIndex(self, index:QtCore.QModelIndex, is_hidden:bool=True):

		source_index = self.mapToSource(index.siblingAtColumn(0))
		new_is_hidden = not source_index.data(binviewitems.BSBinColumnInfoRole.IsHiddenRole)
		return self.setData(index, new_is_hidden, binviewitems.BSBinColumnInfoRole.IsHiddenRole)


	@QtCore.Slot(QtCore.QModelIndex)
	def toggleBinColumnVisibiltyForIndex(self, index:QtCore.QModelIndex):
		
		is_hidden = self.binColumnIsHiddenForIndex(index)
		self.setBinColumnVisibleForIndex(index, is_hidden)

	@QtCore.Slot(QtCore.QModelIndex)
	def removeBinColumnForIndex(self, index:QtCore.QModelIndex):

		if not self.userCanDelete(index) or not index.isValid():
			# Nice try fella
			return
		
		src_idx = self.mapToSource(index)

		if not src_idx.isValid():
			print("Map to source returned invalid index")
			return False
		
		print(f"Source model to remove row {src_idx.row()}: {src_idx.data(QtCore.Qt.ItemDataRole.DisplayRole)}")

		self.sourceModel().removeRow(src_idx.row(), src_idx.parent())
	
#def removeRow(self, row:int, /, parent:QtCore.QModelIndex) -> bool:
#	
#	if parent.isValid():
#		return False
#
#	src_idx = self.mapToSource(self.index(row, 0, parent))
#
#	if not src_idx.isValid():
#		print("Map to source returned invalid index")
#		return False
#	
#	print(f"Source model to remove row {src_idx.row()}: {src_idx.data(QtCore.Qt.ItemDataRole.DisplayRole)}")
#
#	self.sourceModel().removeRow(src_idx.row(), src_idx.parent())
#
#	return True


	def setBinColumnVisibleForIndex(self, index:QtCore.QModelIndex, is_visible:bool=True):
		self.setBinColumnHiddenForIndex(index, not is_visible)

	def userCanDelete(self, index:QtCore.QModelIndex) -> bool:
		"""Rules for user-deletable field"""

		return self.mapToSource(index).data(binviewitems.BSBinColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		"""
		Editor proxy index data uses (row,feature) to access editor bin column data, and (row,0) for bin column info's data roles
		
		Example data model access: `self.index(5, 0).data(binviewitems.BSBinColumnInfoRole.IsHiddenRole)`  
		Example editor proxy access: `self.index(5,  BSBinViewColumnEditorFeature.VisibilityColumn).data(QtCore.Qt.ItemDataRole.DecorationRole)`
		"""

		
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

			# Allow delete if user field
			if self.userCanDelete(proxyIndex):
				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove)
			else:
				return QtGui.QIcon()
		
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
		print("updateRowForIndex says HEEE")

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