from __future__ import annotations
import typing
from PySide6 import QtCore
import avbutils

from . import viewmodelitems
from ..binview import binviewmodel, binviewitems

class BSBinViewProxyModel(QtCore.QSortFilterProxyModel):
	"""QSortFilterProxyModel that implements bin view settings and filters"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Sort mimicking Avid natural sorting (9 before 10, etc)
		self._sort_collator = QtCore.QCollator()
		self._sort_collator.setNumericMode(True)
		self._sort_collator.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

		self._filter_bin_display_items = avbutils.BinDisplayItemTypes(0)
		self._filter_search_text       = ""

		self._sift_options = []
		self._sift_enabled = False

		self._use_binview  = True
		self._use_filters  = True

		self.setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)
		self.setSourceModel(BSBinItemViewModel())

	def setSourceModel(self, sourceModel:BSBinItemViewModel):

		if self.sourceModel() == sourceModel:
			return
		
		# Disconnect old sigs
		if self.sourceModel():
			self.sourceModel().headerDataChanged.disconnect(self.invalidateColumnsFilter)

		# Invalidate column filters on header data change (label/visibility edited via column editor)
		sourceModel.headerDataChanged.connect(self.invalidateColumnsFilter)



		return super().setSourceModel(sourceModel)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		"""Filter rows based on all the applicable sift/bin display/search stuff"""

		if not self._use_filters:
			return False

		try:
			return all((
				self.binDisplayFilter(source_row, source_parent),
	#			self.binSiftFilter(source_row, source_parent),
	#			self.searchTextFilter(source_row, source_parent),
			))
		except Exception as e:
			import logging
			logging.getLogger(__name__).error("Error filtering: %s", str(e))
			return True
		
		# I just feel weird not having this somewhere lol even though it does nothing
		return super().filterAcceptsRow(source_row, source_parent)
		
	
	def filterAcceptsColumn(self, source_column:int, source_parent:QtCore.QModelIndex) -> bool:
		
		# Pass through if BinView is disabled, or looking up a child element (makes no sense)
		if not self._use_binview or source_parent.isValid():
			return super().filterAcceptsColumn(source_column, source_parent)
			
		return not self.sourceModel().headerData(source_column, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+3)

		
		#return super().filterAcceptsRow(source_row, source_parent)
	
	def binDisplayFilter(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		"""Filter rows based on item type (via Bin Display settings)"""

		# Determine BinItemType column index from the source model (since it could be hidden)
		# NOTE: Once this is exclusively an AVB proxy model, won't need the `try`
		try:
			item_type_header_index = next(c
				for c in range(self.sourceModel().columnCount(source_parent))
				if self.sourceModel().headerData(c, QtCore.Qt.Orientation.Horizontal, role=binviewitems.BSBinColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.BinItemIcon
			)

		except StopIteration:
			# TODO: Pass through exception -- in AVB the type should definitely be available
			return super().filterAcceptsRow(source_row, source_parent)
		
		# Get the item type from the source moddel
		src_index = self.sourceModel().index(source_row, item_type_header_index, source_parent)
		item_types = src_index.data(viewmodelitems.BSBinItemDataRoles.BSItemType)
		import logging
		logging.getLogger(__name__).error("Got %s", repr(item_types))
		print("Got ", item_types)

		if isinstance(item_types, avbutils.BinDisplayItemTypes):
#			print(f"{item_types=} in {self._filter_bin_display_items=}")
			return bool(item_types in self._filter_bin_display_items)
		else:
			raise ValueError(f"Invalid data type `{type(item_types).__name__}` for filter (expected `BinDisplayItemTypes`)")
	
	def searchTextFilter(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		"""Filter rows based on display text"""

		if not self._filter_search_text:
			return True

		search_text = self._filter_search_text.casefold()
		
		for source_col in range(self.sourceModel().columnCount()):

			# TODO: For later: ignore hidden columns
			if not self.filterAcceptsColumn(source_col, source_parent):
				continue

			source_text = self.sourceModel().data(self.sourceModel().index(source_row, source_col, source_parent), QtCore.Qt.ItemDataRole.DisplayRole) or ""
			if search_text in source_text.casefold():
				return True
		
		return False
	
	def binSiftFilter(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self._sift_enabled or source_parent.isValid():
			return True
		
		row_data: dict[str,str] = {}

		for source_col in range(self.sourceModel().columnCount()):

			col_is_hidden = self.sourceModel().headerData(source_col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+3)

			if col_is_hidden:
				#print("Skip hidden col", source_col)
				continue

			col_name = self.sourceModel().headerData(source_col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)
			col_text = self.sourceModel().data(self.sourceModel().index(source_row, source_col, source_parent), QtCore.Qt.ItemDataRole.DisplayRole) or ""

			row_data[col_name] = col_text
		
		#return True
		return all(self.siftOptionFilter(s, row_data) for s in self._sift_options[0:3]) and all(self.siftOptionFilter(s, row_data) for s in self._sift_options[3:6])
	
	def siftOptionFilter(self, sift_option:avbutils.bins.BinSiftOption, row_data:dict[str,str]):

		#print(f"{sift_option=}")
		
		if not sift_option.sift_text:
			#print("Sift: No text, returning True")
			return True
		
		elif not sift_option.sift_column or sift_option.sift_column == "None":
			#print("Sift: '", sift_option.sift_column, "' option, returning True")
			return True
		
		#elif sift_option.sift_column not in row_data:
		#	print("****** Sift filter skips ", sift_option.sift_column, " AINT THERE BRUH")
		#	return True
		
		sift_cols = []

		if sift_option.sift_column == "Any":
			sift_cols = list(row_data.keys())
		
		elif sift_option.sift_column not in row_data:
			#print("**** ", sift_option.sift_column, "not there, ignore")
			return True
		
		else:
			sift_cols = [sift_option.sift_column]

		

		# TODO: Timecode ranges contain...

		if sift_option.sift_method == avbutils.bins.BinSiftMethod.CONTAINS:
			#print(f"{sift_option.sift_text=} in {row_data}? {any(sift_option.sift_text.casefold() in row_data[c].casefold() for c in sift_cols)}")
			return any(sift_option.sift_text.casefold() in row_data[c].casefold() for c in sift_cols)
		
		elif sift_option.sift_method == avbutils.bins.BinSiftMethod.BEGINS_WITH:
			#print(any(row_data[c].casefold().startswith(sift_option.sift_text.casefold()) for c in sift_cols), sift_cols, [row_data[c] for c in sift_cols])
			return any(row_data[c].casefold().startswith(sift_option.sift_text.casefold()) for c in sift_cols)
		
		elif sift_option.sift_method == avbutils.bins.BinSiftMethod.MATCHES_EXACTLY:
			return any(row_data[c].casefold() == sift_option.sift_text.casefold() for c in sift_cols)
		else:
			#print("AAAAHA!!!!!!HHTOUIH$GOU$HGOU$NGUONTOU$NOUGNO@$UNGO@$GO$@NGO!!!!!\nHJO%IHJO%INHOITENHOUTNHUON%OGIOIRNMG\n*T)@(%JGO%UGNOI%ML)")
			raise ValueError(f"Unknown sift option {sift_option.sift_method=}")
		
	@QtCore.Slot(bool)
	def setSiftEnabled(self, is_enabled:bool):
		"""Enable sift options"""

		if not self._sift_enabled == is_enabled:
			self._sift_enabled = is_enabled
			self.invalidateRowsFilter()

	def siftEnabled(self) -> bool:
		return self._sift_enabled

	@QtCore.Slot(list)
	def setSiftOptions(self, sift_options:list[avbutils.bins.BinSiftOption]):
		"""Set options for item sifting"""

		self._sift_options = sift_options

		if self._sift_enabled:
			self.invalidateRowsFilter()
	
	@QtCore.Slot(object)
	def setSearchText(self, search_text:str):
		"""Set the text filter"""

		self._filter_search_text = search_text
		self.invalidateRowsFilter()

	
	def lessThan(self, source_left:QtCore.QModelIndex, source_right:QtCore.QModelIndex) -> bool:
		return self._sort_collator.compare(
			source_left.data(self.sortRole()),
			source_right.data(self.sortRole())
		) <= 0	# gt OR EQUAL TO reverses sort even if all thingies are equal, I like it
	
	@QtCore.Slot(object)
	def setBinDisplayItemTypes(self, types:avbutils.BinDisplayItemTypes):

		self._filter_bin_display_items = types
		self.invalidateRowsFilter()
	
	def binDisplayItemTypes(self) -> avbutils.BinDisplayItemTypes:
		return self._filter_bin_display_items
	
	@QtCore.Slot(object)
	def setSearchFilterText(self, search_text:str):
		self._filter_search_text = search_text

	def searchFilterText(self) -> str:
		return self._filter_search_text
	
	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		if is_enabled != self._use_binview:

			self._use_binview = is_enabled
			self.invalidateColumnsFilter()

	@QtCore.Slot(object)
	def setBinFiltersEnabled(self, is_enabled:bool):
		
		if is_enabled != self._use_filters:

			self._use_filters = is_enabled
			self.invalidateRowsFilter()
			
		
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

		import logging
		logging.getLogger(__name__).error("Got bin itme data %s", repr(bin_item_data))

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