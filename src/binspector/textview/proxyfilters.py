from __future__ import annotations
import abc, typing

from PySide6 import QtCore

from ..binitems import binitemtypes
from ..binview import binviewitemtypes

import avbutils

if typing.TYPE_CHECKING:
	from . import textviewproxymodel

class BSAbstractTextViewItemFilter(abc.ABC):

	@abc.abstractmethod
	def filterAcceptsItem(self, proxy_model:textviewproxymodel.BSBTextViewSortFilterProxyModelDEPRECATED, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		pass

class BSBinItemDisplayFilter(BSAbstractTextViewItemFilter):

	DEFAULT_ITEM_TYPES = avbutils.bins.BinDisplayItemTypes.default_items()

	def __init__(self, accepted_item_types:avbutils.bins.BinDisplayItemTypes|None = None):

		super().__init__()

		self._accepted_item_types = accepted_item_types or self.DEFAULT_ITEM_TYPES

	def filterAcceptsItem(self, proxy_model:textviewproxymodel.BSBTextViewSortFilterProxyModelDEPRECATED, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		source_index   = proxy_model.sourceModel().index(source_row, 0, QtCore.QModelIndex())
		bin_item_types = proxy_model.sourceModel().data(source_index, binitemtypes.BSBinItemDataRoles.ItemTypesRole)
		#print("For source index ", source_index, ", got ", bin_item_types)
		#return True

		return bin_item_types in self._accepted_item_types
	
	def setAcceptedItemTypes(self, bin_item_types:avbutils.bins.BinDisplayItemTypes):

#		print("OK set to ", bin_item_types)

		self._accepted_item_types = bin_item_types

	def acceptedItemTypes(self) -> avbutils.bins.BinDisplayItemTypes:

		return self._accepted_item_types

class BSFindInBinFilter(BSAbstractTextViewItemFilter):

	def __init__(self, search_text:str="", case_sensitive:bool=False):

		super().__init__()

		self._search_text    = search_text
		self._case_sensitive = case_sensitive

	def setSearchText(self, search_text:str):

		self._search_text = search_text if self._case_sensitive else search_text.casefold()

	def searchText(self) -> str:

		return self._search_text

	def filterAcceptsItem(self, proxy_model:textviewproxymodel.BSBTextViewSortFilterProxyModelDEPRECATED, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self._search_text:
			return True
		
		# Build search text from visible columns
		for source_col_idx in filter(lambda idx: proxy_model.filterAcceptsColumn(idx, source_parent), range(proxy_model.sourceModel().columnCount(source_parent))):

			src_index           = proxy_model.sourceModel().index(source_row, source_col_idx, source_parent)
			src_filter_data:str = src_index.data(QtCore.Qt.ItemDataRole.DisplayRole) # PRESUMPTUOUS!

			if src_filter_data and self._search_text in (src_filter_data if self._case_sensitive else src_filter_data.casefold()):
				return True

		return False