"""
Manage display delegates
"""
from __future__ import annotations
from ..core.config import BSListViewConfig
from . import binitems
from ..models import viewmodelitems, viewmodels
import avbutils
from PySide6 import QtCore

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from PySide6 import QtWidgets


ITEM_DELEGATES_PER_FIELD_ID = {
	51 : binitems.BSIconLookupItemDelegate, # Clip color
	132: binitems.BSIconLookupItemDelegate, # Marker
	200: binitems.BSIconLookupItemDelegate, # Bin Display Item Type

}
"""Specialized one-off fields"""

ITEM_DELEGATES_PER_FORMAT_ID = {
	avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate,
}
"""Delegate for generic field formats"""

type FormatLookup = dict[avbutils.BinColumnFormat, binitems.BSGenericItemDelegate]
"""Key/Val Lookup For Delegate Lookup"""

type FieldLookup = dict[int, binitems.BSGenericItemDelegate]
"""Key/Val Lookup For Particular Field Lookups"""

class BSDelegateProvider(QtCore.QObject):

	sig_view_changed                  = QtCore.Signal(object)
	sig_default_item_delegate_changed = QtCore.Signal(object)

	sig_field_delegate_changed        = QtCore.Signal(int, object)
	sig_format_delegate_changed       = QtCore.Signal(int, object)

	def __init__(self, view:QtWidgets.QTreeView, **kwargs):

		super().__init__(parent=view)

		# Callables

		self._FIELD_DELEGATE_FACTORIES = {
			51 : binitems.BSIconLookupItemDelegate, # Clip color
			132: binitems.BSIconLookupItemDelegate, # Marker
			200: binitems.BSIconLookupItemDelegate, # Bin Display Item Type

		}
		"""Specialized one-off fields"""

		self._FORMAT_DELEGATE_FACTORIES = {
			avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate,
		}
		"""Delegate for generic field formats"""	


		self._view = view

		# Cached instances
		self._format_delegates :FormatLookup  = dict()
		self._field_delegates  :FieldLookup   = dict()

	def setView(self, view:QtWidgets.QAbstractItemView):

		if self._view == view:
			return
		
		self._format_delegates = dict()
		self._field_delegates  = dict()

		self.sig_view_changed.emit(view)

	def view(self) -> QtWidgets.QAbstractItemView:

		return self._view
	
	def setDefaultItemDelegate(self, delegate:binitems.BSGenericItemDelegate):
		"""Set the view's default item delegate (convenience for view's `setItemDelegate()` method)"""

		if self._view.itemDelegate() == delegate:
			return
		
		self._view.setItemDelegate(delegate)
		self.sig_default_item_delegate_changed.emit(delegate)

	def defaultItemDelegate(self, index:QtCore.QModelIndex|None=None) -> binitems.BSGenericItemDelegate:
		"""Return the view's default item delegate (convenience passthrough for view's `itemDelegate()` method)"""

		if index is not None:
			return self._view.itemDelegate(index)
		
		return self._view.itemDelegate()
	
	def setDelegateForFormat(self, column_format_id:avbutils.bins.BinColumnFormat, delegate:binitems.BSGenericItemDelegate):

		if column_format_id in self._format_delegates and self._format_delegates[column_format_id] == delegate:
			return

		self._format_delegates[column_format_id] = delegate

		self.sig_format_delegate_changed.emit(column_format_id, delegate)

	def setDelegateForField(self, column_field_id:int, delegate:binitems.BSGenericItemDelegate):

		if column_field_id in  self._field_delegates and self._field_delegates[column_field_id] == delegate:
			return

		self._field_delegates[column_field_id] = delegate
		self.sig_field_delegate_changed.emit(column_field_id, delegate)

	def delegateForColumn(self,
		logical_column_index:int,
		*args,
		orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal,
		unique_instance:bool=False
	) -> binitems.BSGenericItemDelegate:

		model  = self._view.model()

		format = model.headerData(logical_column_index, orientation, viewmodelitems.BSBinColumnDataRoles.BSDataFormat)
		field  = model.headerData(logical_column_index, orientation, viewmodelitems.BSBinColumnDataRoles.BSColumnID)

		if unique_instance:

			if field in self._FIELD_DELEGATE_FACTORIES:
				return self._FIELD_DELEGATE_FACTORIES[field]
			
			elif format in self._FORMAT_DELEGATE_FACTORIES[format]:
				return self._FORMAT_DELEGATE_FACTORIES[format]
			
			else:
				return self.defaultItemDelegate()
		
			
		else:
		
			if field in self._field_delegates:
				return self._field_delegates[field]
			
			elif format in self._format_delegates:
				return self._format_delegates[format]
			

			elif field in self._FIELD_DELEGATE_FACTORIES:

				new_del = self._FIELD_DELEGATE_FACTORIES[field]()
				self._field_delegates[field] = new_del
				
				return new_del
			
			elif format in self._FORMAT_DELEGATE_FACTORIES:

				new_del = self._FORMAT_DELEGATE_FACTORIES[format]()
				self._format_delegates[format] = new_del
				
				return new_del
			
			else:
				return self.defaultItemDelegate()
		
		raise RuntimeError("Wat from delegate_lookup")