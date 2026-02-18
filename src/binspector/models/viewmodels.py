from __future__ import annotations
import typing
from PySide6 import QtCore
import avbutils

from . import viewmodelitems
from ..binview import binviewmodel, binviewitems

class BSBinItemViewModel(QtCore.QAbstractItemModel):
	"""A view model for timelines"""


	def __init__(self):

		super().__init__()

		self._frame_locations:list[tuple[int,int]] = []
		"""List of frame view mode position tuples `(x:int, y:int)`"""

		self._bin_items:list[dict[str, viewmodelitems.LBAbstractViewItem]] = []
		"""List of view items by key"""

		self._headers:list[viewmodelitems.LBAbstractViewHeaderItem] = []
		"""List of view headers"""

		self._header_model:binviewmodel.BSBinViewModel = binviewmodel.BSBinViewModel()

	def supportedDropActions(self):
		return super().supportedDropActions() | QtCore.Qt.DropAction.MoveAction
	
	def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
		return super().moveRows(sourceParent, sourceRow, count, destinationParent, destinationChild)
	
	def rowCount(self, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Number of bin items"""

		if parent.isValid():
			return 0
		
		return len(self._bin_items)
	
	def columnCount(self, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Number of available columns"""

		if parent.isValid():
			return 0
		
		return self._header_model.rowCount(parent)

	def parent(self, /, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Get the parent of the given bin item (invalid for now -- flat model)"""

		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Get a handle to an item field"""

		if parent.isValid():
			return QtCore.QModelIndex()

		return self.createIndex(row, column)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:binviewitems.BSBinViewColumnInfo) -> typing.Any:
		"""Get the data for the given role of a specified column index"""

		if not orientation == QtCore.Qt.Orientation.Horizontal:
			return None
		
		return self._header_model.index(section, 0, QtCore.QModelIndex()).data(role)
		
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		"""Get the data for the given role of a specified item index"""

		if not index.isValid():
			return None
		
		# Get the Bin Item
		bin_item_data = self._bin_items[index.row()]

		#import logging
		#logging.getLogger(__name__).error("Got bin itme data %s", repr(bin_item_data))

		# Do row stuff first
		if role == viewmodelitems.BSBinItemDataRoles.BSItemName:
			
			return bin_item_data.get(avbutils.bins.BinColumnFieldIDs.Name).data(QtCore.Qt.ItemDataRole.DisplayRole)
		
		elif role == viewmodelitems.BSBinItemDataRoles.BSFrameCoordinates:
			return self._frame_locations[index.row()]
		
		elif role == viewmodelitems.BSBinItemDataRoles.BSClipColor:
			return bin_item_data.get(avbutils.BinColumnFieldIDs.Color).raw_data()#.data(QtCore.Qt.ItemDataRole.UserRole)
		
		elif role == viewmodelitems.BSBinItemDataRoles.BSItemType:
			return bin_item_data.get(avbutils.BinColumnFieldIDs.BinItemIcon).raw_data()#.data(QtCore.Qt.ItemDataRole.UserRole)
		
		elif role == viewmodelitems.BSBinItemDataRoles.BSScriptNotes:
			return self._getUserColumnItem(index, user_column_name="Comments", role=QtCore.Qt.ItemDataRole.DisplayRole)

		# For user fields: Look up the thingy
		field_id      = self.headerData(index.column(), QtCore.Qt.Orientation.Horizontal, binviewitems.BSBinColumnInfoRole.FieldIdRole)
		#print("Field ID is ", field_id)

		if field_id not in bin_item_data:
			#print(field_id, "Not here in ", list(bin_item_data.keys()))
			return None
		
		elif field_id == avbutils.bins.BinColumnFieldIDs.User:

			# Look up user field
			field_name = self.headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)

			if field_name not in bin_item_data.get(field_id):
				return None

			return bin_item_data.get(field_id).get(field_name).data(role)

		return bin_item_data.get(field_id).data(role)
	
	def _getUserColumnItem(self, index:QtCore.QModelIndex, /, user_column_name:str, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole) -> typing.Any:
		"""Return the string associated with a specified user column name"""

		# NOTE: Add this to avbutils.bins.BinDataColumnFormats or whatever?
		avbutils.bins.BinColumnFieldIDs.User

		bin_item_data = self._bin_items[index.row()]
		
		if avbutils.bins.BinColumnFieldIDs.User not in bin_item_data:
			return None
		
		user_data = self._bin_items[index.row()][avbutils.bins.BinColumnFieldIDs.User]

		if user_column_name not in user_data:
			return None
		
		return user_data[user_column_name].data(role)


		field_name = self.headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)

	
	def flags(self, index:QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
		
		# Append flag `QtCore.Qt.ItemFlag.ItemNeverHasChildren` for flat list optimization
		
		if index.isValid():
			return super().flags(index) | QtCore.Qt.ItemFlag.ItemNeverHasChildren
		
		return super().flags(index)
	
	def clear(self):
		"""Clear and reset the model"""

		self.beginResetModel()
		
		self._bin_items = []
		self._frame_locations = []
		self._headers = []
		
		self.endResetModel()

	def addBinItem(self, bin_item:dict[str,viewmodelitems.LBAbstractViewItem], frame_position:tuple[int,int]|None=None) -> bool:
		"""Binspecific: Add a bin item"""

		return self.addBinItems([bin_item], [frame_position])
		
	def addBinItems(self, bin_items:list[dict[str,viewmodelitems.LBAbstractViewItem]], frame_positions:list[tuple[int,int]]|None=None) -> bool:
		"""Binspecific: Add a bin items"""

		# Ignore empty lists
		if not len(bin_items):
			return False
		
		if not frame_positions:
			frame_positions = [(-30000,-30000)] * len(bin_items)
		
		elif not len(bin_items) == len(frame_positions):
			raise ValueError(f"Frame positions cound ({len(frame_positions)}) does not match bin items count ({len(bin_items)})")
		
		row_start = len(self._bin_items)
		row_end   = row_start + len(bin_items) - 1 # Row end is inclusive

		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)
		#print("Adding", bin_items)
		self._bin_items.extend(bin_items)
		self._frame_locations.extend(frame_positions)
		
		self.endInsertRows()

		return True
	
	###

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):

		if self._header_model == bin_view_model:
			return
		
		# TODO: Disconnect from old
		
		self.beginResetModel()

		self._header_model= bin_view_model

		self._header_model.dataChanged.connect(self.notifyColumnChanged)
		self._header_model.rowsAboutToBeRemoved.connect(self.notifyColumnsAboutToBeRemoved)
		self._header_model.rowsRemoved.connect(self.notifyColumnsRemoved)
		self._header_model.rowsAboutToBeInserted.connect(self.notifyColumnsAboutToBeInserted)
		self._header_model.rowsInserted.connect(self.notifyColumnsInserted)
		self._header_model.rowsAboutToBeMoved.connect(self.notifyColumnsAboutToBeMoved)
		self._header_model.rowsMoved.connect(self.notifyColumnsMoved)

		self.endResetModel()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def notifyColumnsAboutToBeMoved(self, source_parent:QtCore.QModelIndex, source_first:int, source_last:int, dest_parent:QtCore.QModelIndex, dest_first:int):

		self.beginMoveColumns(QtCore.QModelIndex(), source_first, source_last, QtCore.QModelIndex(), dest_first)

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def notifyColumnsMoved(self, source_parent:QtCore.QModelIndex, source_first:int, source_last:int, dest_parent:QtCore.QModelIndex, dest_first:int):
		
		self.endMoveColumns()
		
	@QtCore.Slot(QtCore.QModelIndex,QtCore.QModelIndex,QtCore.Qt.ItemDataRole)
	def notifyColumnChanged(self, header_index_start:QtCore.QModelIndex, header_index_end:QtCore.QModelIndex, roles:list[QtCore.Qt.ItemDataRole]|None=None):
		
		# Map
		logical_col_start = header_index_start.row()
		logical_col_end   = header_index_end.row()

		self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, logical_col_start, logical_col_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def notifyColumnsAboutToBeRemoved(self, parent:QtCore.QModelIndex, header_col_start, header_col_end):

		if parent.isValid():
			return
		
		self.beginRemoveColumns(QtCore.QModelIndex(), header_col_start, header_col_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def notifyColumnsRemoved(self, parent:QtCore.QModelIndex, header_col_start, header_col_end):

		if parent.isValid():
			return

		self.endRemoveColumns()


	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def notifyColumnsAboutToBeInserted(self, parent:QtCore.QModelIndex, header_col_start, header_col_end):

		if parent.isValid():
			return
		
		self.beginInsertColumns(QtCore.QModelIndex(), header_col_start, header_col_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def notifyColumnsInserted(self, parent:QtCore.QModelIndex, header_col_start, header_col_end):

		if parent.isValid():
			return
		
		self.endInsertColumns()