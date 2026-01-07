"""
Manage display delegates
"""
from __future__ import annotations
from ..core.config import BSListViewConfig
from . import binitems
from ..models import viewmodelitems, viewmodels
import avbutils
from PySide6 import QtCore

import typing
if typing.TYPE_CHECKING:
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
	"""(`FieldID`, `NewDelegate`)"""

	sig_format_delegate_changed       = QtCore.Signal(int, object)
	"""(`FormatID`, `NewDelegate`)"""

	def __init__(self, view:QtWidgets.QAbstractItemView, **kwargs):

		super().__init__(parent=view)

		# Callables

		self._FIELD_DELEGATE_FACTORIES: FieldLookup = {
			51 : binitems.BSIconLookupItemDelegate, # Clip color
			132: binitems.BSIconLookupItemDelegate, # Marker
			200: binitems.BSIconLookupItemDelegate, # Bin Display Item Type

		}
		"""Specialized one-off fields"""

		self._FORMAT_DELEGATE_FACTORIES: FormatLookup = {
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

	def delegates(self) -> set[binitems.BSGenericItemDelegate]:

		import itertools
		return set(itertools.chain(self._format_delegates.values(), self._field_delegates.values()))
	
	def delegateForFormat(self, format:avbutils.bins.BinColumnFormat, /, default_ok:bool=True) -> binitems.BSGenericItemDelegate|None:
		"""Return the delegate for the given `avbutils.bins.BinColumnFormat"""

		# Return default delegate instance if unknown
		if format not in self._format_delegates and format not in self._FORMAT_DELEGATE_FACTORIES:
			return self.defaultItemDelegate() if default_ok else None
		
		# Cache delegate instance if there's a factory for it
		if format not in self._format_delegates:
			self._format_delegates[format] = self._FORMAT_DELEGATE_FACTORIES[format]()

		# Return delegate instance
		return self._format_delegates[format]
	
	def delegateForField(self, field:int, /, default_ok:bool=True) -> binitems.BSGenericItemDelegate:
		"""Return the delegate for the given `avbutils.bins.BIN_COLUMN_ROLES`"""

		# Return default delegate instance if unknown
		if field not in self._field_delegates and field not in self._FIELD_DELEGATE_FACTORIES:
			return self.defaultItemDelegate() if default_ok else None
		
		# Cache delegate instance if there's a factory for it
		if field not in self._field_delegates:
			self._field_delegates[field] = self._FIELD_DELEGATE_FACTORIES[field]()

		# Return delegate instance
		return self._field_delegates[field]
		

	def delegateForColumn(self,
		logical_column_index:int,
		*args,
		orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal,
		unique_instance:bool=False
	) -> binitems.BSGenericItemDelegate:
		"""Provide a delegate for a given logical column index of the view's model"""

		model  = self._view.model()

		format = model.headerData(logical_column_index, orientation, viewmodelitems.BSBinColumnDataRoles.BSDataFormat)
		field  = model.headerData(logical_column_index, orientation, viewmodelitems.BSBinColumnDataRoles.BSColumnID)

		if unique_instance:

			if field in self._FIELD_DELEGATE_FACTORIES:
				return self._FIELD_DELEGATE_FACTORIES[field]()
			
			elif format in self._FORMAT_DELEGATE_FACTORIES[format]:
				return self._FORMAT_DELEGATE_FACTORIES[format]()
			
			else:
				return self.defaultItemDelegate()
		
			
		else:

			if (delegate := self.delegateForField(field, default_ok=False)) is not None:
				return delegate
			
			elif (delegate := self.delegateForFormat(format, default_ok=False)) is not None:
				return delegate
			
			else:
				return self.defaultItemDelegate()
		