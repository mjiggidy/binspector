from ..binitems import binitemtypes
from ..binview import binviewitemtypes
from ..models import viewmodels

from . import textviewmodel

import avbutils
from PySide6 import QtCore

class BSBTextViewSortFilterProxyModel(QtCore.QSortFilterProxyModel):
	"""The New One For The New Thing"""

	def __init__(self, *args, text_view_model:textviewmodel.BSTextViewModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setSourceModel(text_view_model if text_view_model else textviewmodel.BSTextViewModel())

	def setSourceModel(self, sourceModel:textviewmodel.BSTextViewModel):

		if self.sourceModel() == sourceModel:
			return

		if not isinstance(sourceModel, textviewmodel.BSTextViewModel):
			raise ValueError(f"Source model must be `BSTextViewModel`; got {repr(sourceModel)}")
		
		sourceModel.headerDataChanged.connect(self.binColumnDataChanged)
		
		super().setSourceModel(sourceModel)

	@QtCore.Slot(QtCore.Qt.Orientation, int, int)
	def binColumnDataChanged(self, orientation:QtCore.Qt.Orientation, first:int, last:int):
		
		# NOTE: I feel weird calling `begin` AFTER the data has changed

		self.beginFilterChange()
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Columns)


	def filterAcceptsColumn(self, source_column:int, source_parent:QtCore.QModelIndex) -> bool:

		if source_parent.isValid():
			return False
		
		return not self.sourceModel().headerData(source_column, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)




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
		self.setSourceModel(viewmodels.BSBinItemViewModel())

	def setSourceModel(self, sourceModel:viewmodels.BSBinItemViewModel):

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
				self.binSiftFilter(source_row, source_parent),
				self.searchTextFilter(source_row, source_parent),
			))
		except Exception as e:
			#import logging
			#logging.getLogger(__name__).error("Error filtering: %s", str(e))
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
				if self.sourceModel().headerData(c, QtCore.Qt.Orientation.Horizontal, role=binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.BinItemIcon
			)

		except StopIteration:
			# TODO: Pass through exception -- in AVB the type should definitely be available
			return super().filterAcceptsRow(source_row, source_parent)

		# Get the item type from the source moddel
		src_index = self.sourceModel().index(source_row, item_type_header_index, source_parent)
		item_types = src_index.data(binitemtypes.BSBinItemDataRoles.ItemTypesRole)

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

			col_is_hidden = self.sourceModel().headerData(source_col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

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
		) <= 0 # gt OR EQUAL TO reverses sort even if all thingies are equal, I like it

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