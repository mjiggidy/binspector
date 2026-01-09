"""
Manage display delegates
"""
from __future__ import annotations
from ..core.config import BSListViewConfig
from . import itemdelegates
from ..models import viewmodelitems, viewmodels
import avbutils
from PySide6 import QtCore

import typing
if typing.TYPE_CHECKING:
	from PySide6 import QtWidgets

type FormatLookup = dict[avbutils.BinColumnFormat, itemdelegates.BSGenericItemDelegate]
"""Key/Val Lookup For Delegate Lookup"""

type FieldLookup = dict[int, itemdelegates.BSGenericItemDelegate]
"""Key/Val Lookup For Particular Field Lookups"""

class BSDelegateProvider(QtCore.QObject):

	sig_view_changed                  = QtCore.Signal(object)
	sig_default_item_delegate_changed = QtCore.Signal(object)

	sig_field_delegate_changed        = QtCore.Signal(int, object)
	"""(`FieldID`, `NewDelegate`)"""

	sig_format_delegate_changed       = QtCore.Signal(int, object)
	"""(`FormatID`, `NewDelegate`)"""

	def __init__(self, view:QtWidgets.QAbstractItemView, default_delegate:itemdelegates.BSGenericItemDelegate|None=None):

		super().__init__(parent=view)

		# Callables

		self._FIELD_DELEGATE_FACTORIES: FieldLookup = {
			51 : itemdelegates.BSIconLookupItemDelegate, # Clip color
			132: itemdelegates.BSIconLookupItemDelegate, # Marker
			200: itemdelegates.BSIconLookupItemDelegate, # Bin Display Item Type

		}
		"""Specialized one-off fields"""

		self._FORMAT_DELEGATE_FACTORIES: FormatLookup = {
			avbutils.BinColumnFormat.TIMECODE: itemdelegates.LBTimecodeItemDelegate,
		}
		"""Delegate for generic field formats"""	


		self._view = view

		# Cached instances
		self._format_delegates :FormatLookup  = dict()
		self._field_delegates  :FieldLookup   = dict()
		
		self.setDefaultItemDelegate(default_delegate or itemdelegates.BSGenericItemDelegate())

	@QtCore.Slot()
	def refreshDelegates(self):
		"""Update all delegates in the current view"""

		if not self._view.model():
			return

		for col in range(self._view.model().columnCount()):
			self.setDelegateForColumn(col, self.delegateForColumn(col))
	
	def setView(self, view:QtWidgets.QAbstractItemView):
		"""Set the `QAbstractItemview` which will use the delegates"""

		if self._view == view:
			return
		
		self._format_delegates = dict()
		self._field_delegates  = dict()

		self.sig_view_changed.emit(view)

	def view(self) -> QtWidgets.QAbstractItemView:
		"""The view for which the delegates will be used"""

		return self._view
	
	def setDefaultItemDelegate(self, delegate:itemdelegates.BSGenericItemDelegate):
		"""Set the view's default item delegate (convenience for view's `setItemDelegate()` method)"""

		if self._view.itemDelegate() == delegate:
			return
		
		self._view.setItemDelegate(delegate)
		self.sig_default_item_delegate_changed.emit(delegate)

	def defaultItemDelegate(self, index:QtCore.QModelIndex|None=None) -> itemdelegates.BSGenericItemDelegate:
		"""Return the view's default item delegate (convenience passthrough for view's `itemDelegate()` method)"""

		if index is not None:
			return self._view.itemDelegate(index)
		
		return self._view.itemDelegate()
	
	def setDelegateForFormat(self, column_format_id:avbutils.bins.BinColumnFormat, delegate:itemdelegates.BSGenericItemDelegate):
		"""Set the item delegate for a given format"""

		if column_format_id in self._format_delegates and self._format_delegates[column_format_id] == delegate:
			return

		self._format_delegates[column_format_id] = delegate

		self.sig_format_delegate_changed.emit(column_format_id, delegate)

	def setDelegateForField(self, column_field_id:int, delegate:itemdelegates.BSGenericItemDelegate):
		"""Set the item delegate for a given field"""

		if column_field_id in  self._field_delegates and self._field_delegates[column_field_id] == delegate:
			return

		self._field_delegates[column_field_id] = delegate
		self.sig_field_delegate_changed.emit(column_field_id, delegate)
	
	def delegateForFormat(self, format:avbutils.bins.BinColumnFormat, /, default_ok:bool=True) -> itemdelegates.BSGenericItemDelegate|None:
		"""Return the delegate for the given `avbutils.bins.BinColumnFormat"""

		# Return default delegate instance if unknown
		if format not in self._format_delegates and format not in self._FORMAT_DELEGATE_FACTORIES:
			return self.defaultItemDelegate() if default_ok else None
		
		# Cache delegate instance if there's a factory for it
		if format not in self._format_delegates:
			self._format_delegates[format] = self._FORMAT_DELEGATE_FACTORIES[format]()

		# Return delegate instance
		return self._format_delegates[format]
	
	def delegateForField(self, field:int, /, default_ok:bool=True) -> itemdelegates.BSGenericItemDelegate:
		"""Return the delegate for the given `avbutils.bins.BIN_COLUMN_ROLES`"""

		# Return default delegate instance if unknown
		if field not in self._field_delegates and field not in self._FIELD_DELEGATE_FACTORIES:
			return self.defaultItemDelegate() if default_ok else None
		
		# Cache delegate instance if there's a factory for it
		if field not in self._field_delegates:
			self._field_delegates[field] = self._FIELD_DELEGATE_FACTORIES[field]()

		# Return delegate instance
		return self._field_delegates[field]
	
	def setDelegateForColumn(self, logical_column_index:int, item_delegate:itemdelegates.BSGenericItemDelegate):

		if self._view.itemDelegateForColumn(logical_column_index) == item_delegate:
			return
		
		import logging
		logging.getLogger(__name__).debug("Setting visual col %s to %s with padding %s", str(self._view.header().visualIndex(logical_column_index)), str(item_delegate), str(item_delegate.itemPadding()))
		
		self._view.setItemDelegateForColumn(logical_column_index, item_delegate)
		
	def delegateForColumn(self,
		logical_column_index:int,
		*args,
		orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal,
		unique_instance:bool=False
	) -> itemdelegates.BSGenericItemDelegate:
		"""Provide a delegate for a given logical column index of the view's model"""

		model  = self._view.model()

		format = model.headerData(logical_column_index, orientation, viewmodelitems.BSBinColumnDataRoles.BSDataFormat)
		field  = model.headerData(logical_column_index, orientation, viewmodelitems.BSBinColumnDataRoles.BSColumnID)

		if unique_instance:

			if field in self._FIELD_DELEGATE_FACTORIES:
				return self._FIELD_DELEGATE_FACTORIES[field]()
			
			elif format in self._FORMAT_DELEGATE_FACTORIES:
				return self._FORMAT_DELEGATE_FACTORIES[format]()
			
			else: # TODO: UUUHHH PROLLY NOT
				return self.defaultItemDelegate().__class__()
			
		else:

			if (delegate := self.delegateForField(field, default_ok=False)) is not None:
				return delegate
			
			elif (delegate := self.delegateForFormat(format, default_ok=False)) is not None:
				return delegate
			
			else:
				return self.defaultItemDelegate()

	def delegates(self) -> set[itemdelegates.BSGenericItemDelegate]:
		"""Get all known item delegate instances (does not include unique instances)"""

		import itertools
		return set(itertools.chain(self._format_delegates.values(), self._field_delegates.values()))