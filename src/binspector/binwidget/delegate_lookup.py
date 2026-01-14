"""
Manage display delegates
"""
from __future__ import annotations
import typing
import avbutils

from PySide6 import QtCore

from . import itemdelegates

from ..models import viewmodelitems
from ..core   import icon_providers
from ..res    import icons_binitems

if typing.TYPE_CHECKING:
	from PySide6 import QtWidgets

type FormatLookup = dict[avbutils.BinColumnFormat, itemdelegates.BSGenericItemDelegate]
"""Key/Val Lookup For Delegate Lookup"""

type FieldLookup = dict[int, itemdelegates.BSGenericItemDelegate]
"""Key/Val Lookup For Particular Field Lookups"""

class BSBinColumnDelegateProvider(QtCore.QObject):
	"""
	Item delegate provider for binwidget treeview columns.
	Allows delegate lookup based generic field type or bespoke individual fields
	"""

	sig_view_changed                  = QtCore.Signal(object)
	sig_default_item_delegate_changed = QtCore.Signal(object)

	sig_field_delegate_changed        = QtCore.Signal(int, object)
	"""(`FieldID`, `NewDelegate`)"""

	sig_format_delegate_changed       = QtCore.Signal(int, object)
	"""(`FormatID`, `NewDelegate`)"""

	def __init__(self, view:QtWidgets.QAbstractItemView, default_delegate:itemdelegates.BSGenericItemDelegate|None=None):

		super().__init__(parent=view)

		# Callables

		self._FIELD_DELEGATE_REGISTRY: FieldLookup = {
			51 : itemdelegates.BSIconLookupItemDelegate(
				icon_provider=icon_providers.BSPalettedClipColorIconProvider()
			), # Clip color
			132: itemdelegates.BSIconLookupItemDelegate(), # Marker
			200: itemdelegates.BSIconLookupItemDelegate(
				icon_provider=icon_providers.BSPalettedBinItemTypeIconProvider()
			), # Bin Display Item Type

		}
		"""Specialized one-off fields"""

		self._FORMAT_DELEGATE_REGISTRY: FormatLookup = {
#			avbutils.BinColumnFormat.TIMECODE: itemdelegates.LBTimecodeItemDelegate(),
		}
		"""Delegate for generic field formats"""

		self._view = view

		# Cached instances -- TODO: Combine this with registry
		self._format_delegates :FormatLookup  = dict()
		self._field_delegates  :FieldLookup   = dict()
		
		self.setDefaultItemDelegate(default_delegate or itemdelegates.BSGenericItemDelegate())

		# Setup icons
		item_type_icon_provider:icon_providers.BSPalettedBinItemTypeIconProvider = self._FIELD_DELEGATE_REGISTRY[200].iconProvider()
		item_type_icon_provider.setIconPathForBinItemType(avbutils.bins.BinDisplayItemTypes.MASTER_CLIP|avbutils.bins.BinDisplayItemTypes.USER_CLIP, ":/icons/binitems/item_masterclip.svg")
	
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
		if format not in self._format_delegates and format not in self._FORMAT_DELEGATE_REGISTRY:
			return self.defaultItemDelegate() if default_ok else None
		
		# Cache delegate instance if there's a factory for it
		if format not in self._format_delegates:
			self._format_delegates[format] = self._FORMAT_DELEGATE_REGISTRY[format]()

		# Return delegate instance
		return self._format_delegates[format]
	
	def delegateForField(self, field:int, /, default_ok:bool=True) -> itemdelegates.BSGenericItemDelegate:
		"""Return the delegate for the given `avbutils.bins.BIN_COLUMN_ROLES`"""

		# Return default delegate instance if unknown
		if field not in self._field_delegates and field not in self._FIELD_DELEGATE_REGISTRY:
			return self.defaultItemDelegate() if default_ok else None
		
		# Cache delegate instance if there's a factory for it
		if field not in self._field_delegates:
			self._field_delegates[field] = self._FIELD_DELEGATE_REGISTRY[field]

		# Return delegate instance
		return self._field_delegates[field]
	
	def setDelegateForColumn(self, logical_column_index:int, item_delegate:itemdelegates.BSGenericItemDelegate):

		if self._view.itemDelegateForColumn(logical_column_index) == item_delegate:
			return
		
#		import logging
#		logging.getLogger(__name__).debug("Setting visual col %s to %s with padding %s", str(self._view.header().visualIndex(logical_column_index)), str(item_delegate), str(item_delegate.itemPadding()))
		
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

			# Clone whatever the delegate should be
			# NOTE: Cloning is a fancy thing I did from `BSGenericItemDelegate` that I'll regret later probably

			if field in self._FIELD_DELEGATE_REGISTRY:
				return self._FIELD_DELEGATE_REGISTRY[field].clone()
			
			elif format in self._FORMAT_DELEGATE_REGISTRY:
				return self._FORMAT_DELEGATE_REGISTRY[format].clone()
			
			else:
				return self.defaultItemDelegate().clone()
			
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