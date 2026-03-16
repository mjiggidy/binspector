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
	def filterAcceptsItem(self, proxy_model:textviewproxymodel.BSBTextViewSortFilterProxyModel, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		pass

class BSBinItemDisplayFilter(BSAbstractTextViewItemFilter):

	DEFAULT_ITEM_TYPES = avbutils.bins.BinDisplayItemTypes.default_items()

	def __init__(self, accepted_item_types:avbutils.bins.BinDisplayItemTypes|None = None):

		self._accepted_item_types = accepted_item_types or self.DEFAULT_ITEM_TYPES

	def filterAcceptsItem(self, proxy_model:textviewproxymodel.BSBTextViewSortFilterProxyModel, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

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
