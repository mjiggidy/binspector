import typing
from PySide6 import QtCore
import avbutils
from . import viewmodelitems

class LBSortFilterProxyModel(QtCore.QSortFilterProxyModel):
	"""QSortFilterProxyModel that implements natural sorting and such"""

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

		self._use_binview  = False
		self._use_filters  = False

		self.setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		"""Filter rows based on all the applicable sift/bin display/search stuff"""

		if not self._use_filters:
			return super().filterAcceptsRow(source_row, source_parent)

		return all((
			self.binDisplayFilter(source_row, source_parent),
			self.binSiftFilter(source_row, source_parent),
			self.searchTextFilter(source_row, source_parent),
		))
	
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
				if self.sourceModel().headerData(c, QtCore.Qt.Orientation.Horizontal, role=QtCore.Qt.ItemDataRole.UserRole+1) == 200
			)
		except StopIteration:
#			print("Item types not available")
			# TODO: Pass through exception -- in AVB the type should definitely be available
			return super().filterAcceptsRow(source_row, source_parent)
		
		# Get the item type from the source moddel
		src_index = self.sourceModel().index(source_row, item_type_header_index, source_parent)
		item_types = src_index.data(QtCore.Qt.ItemDataRole.UserRole).raw_data()

		if isinstance(item_types, avbutils.BinDisplayItemTypes):
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
			print("**** ", sift_option.sift_column, "not there, ignore")
			return True
		else:
			sift_cols = [sift_option.sift_column]

		

		#print("** NORMAL SIFT: ", sift_option)

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
		#(self.binDisplayItemTypes().__repr__())
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
			
		
class LBTimelineViewModel(QtCore.QAbstractItemModel):
	"""A view model for timelines"""

	def __init__(self):

		super().__init__()

		self._bin_items:list[dict[str, viewmodelitems.LBAbstractViewItem]] = []
		"""List of view items by key"""

		self._headers:list[viewmodelitems.LBAbstractViewHeaderItem] = []
		"""List of view headers"""
	
	def rowCount(self, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Number of bin items"""

		if parent.isValid():
			return 0
		
		return len(self._bin_items)
	
	def columnCount(self, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Number of available columns"""

		if parent.isValid():
			return 0
		
		return len(self._headers)

	def parent(self, /, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Get the parent of the given bin item (invalid for now -- flat model)"""

		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Get a handle to an item field"""

		if parent.isValid():
			return QtCore.QModelIndex()

		return self.createIndex(row, column)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		"""Get the data for the given role of a specified column index"""

		if orientation == QtCore.Qt.Orientation.Horizontal:
			return self._headers[section].data(role)
		
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		"""Get the data for the given role of a specified item index"""

		if not index.isValid():
			return None
		
		timeline   = self._bin_items[index.row()]
		field_name = self._headers[index.column()].field_name()

		if field_name not in timeline:
			return None

		return timeline.get(field_name).data(role)
	
	def fields(self) -> list[str]:
		"""Binspecific: Field names for mapping headers and columns, in order"""

		return [x.field_name() for x in self._headers]
	
	def clear(self):
		"""Clear and reset the model"""

		self.beginResetModel()
		
		self._bin_items = []
		self._headers = []
		
		self.endResetModel()
	
	def addHeader(self, header:viewmodelitems.LBAbstractViewHeaderItem) -> bool:
		"""Binspecific: Add a column header"""
		
		new_idx = len(self._headers)
		
		self.beginInsertColumns(QtCore.QModelIndex(), new_idx, new_idx)
		self._headers.append(header)
		self.endInsertColumns()
		
		return True

	def addBinItem(self, bin_item:dict[str,viewmodelitems.LBAbstractViewItem]) -> bool:
		"""Binspecific: Add a bin item"""

		return self.addBinItems([bin_item])
	
	def addBinItems(self, bin_items:list[dict[str,viewmodelitems.LBAbstractViewItem]]) -> bool:
		"""Binspecific: Add a bin items"""

		# Ignore empty lists
		if not len(bin_items):
			return False
		
		row_start = len(self._bin_items)
		row_end   = row_start + len(bin_items) - 1 # Row end is inclusive

		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)
		self._bin_items.extend(bin_items)
		self.endInsertRows()

		return True