import logging

from PySide6 import QtCore, QtGui
import enum, typing
from ..binview import binviewitemtypes, binviewmodel
from ..res import icons_gui

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

	def setSourceModel(self, bin_view_model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model to edit"""

		if self.sourceModel() == bin_view_model:
			return
		
		self.beginResetModel()

		if self.sourceModel():
			self.sourceModel().disconnect(self)

		super().setSourceModel(bin_view_model)

		logging.getLogger(__name__).debug("SETTING UP EDITOR FOR %s", bin_view_model.binViewName())

		self.sourceModel().rowsAboutToBeRemoved.connect(self.sourceModelAboutToRemoveRows)
		self.sourceModel().rowsRemoved.connect(self.sourceModelRemovedRows)
		
		self.sourceModel().rowsAboutToBeInserted.connect(self.sourceModelAboutToInsertRows)
		self.sourceModel().rowsInserted.connect(self.sourceModelInsertedRows)

		self.sourceModel().rowsAboutToBeMoved.connect(self.sourceModelAboutToMoveRows)
		self.sourceModel().rowsMoved.connect(self.sourceModelMovedRows)

		self.sourceModel().modelAboutToBeReset.connect(self.modelAboutToBeReset)
		self.sourceModel().modelReset.connect(self.modelReset)
		self.sourceModel().layoutChanged.connect(self.layoutChanged)

		self.endResetModel()

	def binViewModel(self) -> binviewmodel.BSBinViewModel:

		return self.sourceModel()
	


	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceModelAboutToMoveRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int, destination:QtCore.QModelIndex, dest_row:int):
		print("He")

		self.beginMoveRows(QtCore.QModelIndex(), row_start, row_end, QtCore.QModelIndex(), dest_row)

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceModelMovedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int, destination:QtCore.QModelIndex, dest_row:int):

		self.endMoveRows()

		

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
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelRemovedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if self.mapFromSource(parent).isValid():
			return
		
		self.endRemoveRows()
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelAboutToInsertRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):
		
		if self.mapFromSource(parent).isValid():
			return
		
		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelInsertedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if self.mapFromSource(parent).isValid():
			return
		
		self.endInsertRows()

	def features(self) -> list[BSBinViewColumnEditorFeature]:

		return list(self._editor_columns)

	def featureForColumn(self, column:int) -> BSBinViewColumnEditorFeature:
		"""Return the editor feature for a given logical column"""

		return self._editor_columns[column]
	
	def featureForIndex(self, index:QtCore.QModelIndex) -> BSBinViewColumnEditorFeature:
		"""Determine editor column feature for a given index"""

		return self.featureForColumn(index.column())
	
	def binViewColumnForIndex(self, index:QtCore.QModelIndex) -> binviewitemtypes.BSBinViewColumnInfo:
		"""Get the `BSBinViewColumnInfo` for a given index"""

		if not index.isValid():
			return None
		
		return self.sourceModel().data(binviewitemtypes.BSBinViewColumnInfoRole.RawColumnInfo)
	
	def binColumnIsHiddenForIndex(self, index:QtCore.QModelIndex) -> bool:
		return self.data(index, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

	def setBinColumnHiddenForIndex(self, index:QtCore.QModelIndex, is_hidden:bool=True):

		source_index = self.mapToSource(index.siblingAtColumn(0))
		new_is_hidden = not source_index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
		return self.setData(index, new_is_hidden, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

	@QtCore.Slot(QtCore.QModelIndex, str)
	def renameColumnForIndex(self, index:QtCore.QModelIndex, name:str) -> bool:

		source_index = self.mapToSource(index.siblingAtColumn(0))
		return self.sourceModel().setData(source_index, name, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

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
	
	@QtCore.Slot()
	def appendUserColumn(self):
		"""Add a user-text column"""

		parent = QtCore.QModelIndex()

		self.sourceModel().insertRow(self.sourceModel().rowCount(parent), parent)
	
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

		return self.mapToSource(index).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User
	
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

		elif feature == BSBinViewColumnEditorFeature.VisibilityColumn:
			
			is_hidden =source_index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
			
			if role == QtCore.Qt.ItemDataRole.DecorationRole:
				return QtGui.QIcon(":/icons/gui/toggle_visibilty_off.svg") if is_hidden else  QtGui.QIcon(":/icons/gui/toggle_visibilty_on.svg")
			if role == QtCore.Qt.ItemDataRole.ToolTipRole:
				return self.tr("<strong>Toggle Column Visibility</strong><br/>This column is currently {is_hidden}").format(is_hidden = self.tr("hidden", "Referring to column visibility") if is_hidden else self.tr("visible",  "Referring to column visibility"))

		elif feature == BSBinViewColumnEditorFeature.DataFormatColumn:

			data_format:avbutils.bins.BinColumnFormat = source_index.data(binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return str(data_format)[0]
			elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
				return self.tr("<strong>Column Data Format</strong><br/>{data_format_name}").format(data_format_name = data_format.name.title())
		
		elif feature == BSBinViewColumnEditorFeature.DeleteColumn:

			can_delete = self.userCanDelete(proxyIndex)

			if role == QtCore.Qt.ItemDataRole.DecorationRole:
				
				# Allow delete if user field
				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove) if can_delete else QtGui.QIcon()
		
			if role == QtGui.Qt.ItemDataRole.ToolTipRole:

				if can_delete:
					return self.tr("<strong>Remove User Column</strong><br/>Remove this user column from the current bin view")
		
	def setData(self, index:QtCore.QModelIndex, value:typing.Any, /, role:QtCore.Qt.ItemDataRole):

		if not super().setData(index, value, role):
			return False
		
		index_start = index.siblingAtColumn(0)
		index_end   = index.siblingAtColumn(self.columnCount(index.parent())-1)

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
	
	def flags(self, index):
		
		flags = QtCore.Qt.ItemFlag(self.DEFAULT_FLAGS)

		# Allow dropping between items (invalid indexes)
		if not index.isValid():
			return QtCore.Qt.ItemFlag.ItemIsDropEnabled
		
		# Column Name Edidiable if user field and we're talkin bout the name column here
		if self.featureForIndex(index) == BSBinViewColumnEditorFeature.NameColumn and index.data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User:
			flags |= QtCore.Qt.ItemFlag.ItemIsEditable
		
		return flags | QtCore.Qt.ItemFlag.ItemIsDragEnabled
	
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		# NOTE: 02 Feb 2026 11:0am: This is officially the dumbest I've been yet.
		# Took me like two weeks to figure out THIS WAS ALL I EVER NEEDED TO DO.

		return self.index(sourceIndex.row(), sourceIndex.column(), sourceIndex.parent())
	
	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if not proxyIndex.isValid():
			return QtCore.QModelIndex()

		return self.sourceModel().index(proxyIndex.row(), proxyIndex.column(), QtCore.QModelIndex())
	
	def supportedDragActions(self) -> QtCore.Qt.DropAction:
		return QtCore.Qt.DropAction.MoveAction
	
	def supportedDropActions(self)-> QtCore.Qt.DropAction:
		return QtCore.Qt.DropAction.MoveAction
	
	def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
		
		source_row_start = self.mapToSource(self.sourceModel().index(sourceRow, 0, QtCore.QModelIndex())).row()
		source_row_dest  = self.mapToSource(self.sourceModel().index(destinationChild, 0, QtCore.QModelIndex())).row()

		#print("GON BE MOVAN FROM ", sourceRow, " TO ", destinationChild)

		return self.sourceModel().moveRows(QtCore.QModelIndex(), source_row_start, count, QtCore.QModelIndex(), source_row_dest)

		#return super().moveRows(sourceParent, sourceRow, count, destinationParent, destinationChild)
	
	def mimeTypes(self):
		return ['application/x-qabstractitemmodeldatalist']
	
	def canDropMimeData(self, data:QtCore.QMimeData, action:QtCore.Qt.DropAction, row:int, column:int, parent:QtCore.QModelIndex):
		
		# Only allow drops *between* items
		# (Pairs with flags() returning ItemFalgs.ItemAcceptsDrops for invalid QModelIndexes)

		return not parent.isValid()