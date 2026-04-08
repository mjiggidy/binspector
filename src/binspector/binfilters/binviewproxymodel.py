from PySide6 import QtCore
from . import abstractfiltermodel
from ..binview import binviewitemtypes

class BSBinViewFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	def __init__(self, *args, bin_columns_model:QtCore.QAbstractItemModel|None=None, is_enabled=True, **kwargs):
		
		super().__init__(*args, is_enabled=is_enabled, **kwargs)

		if bin_columns_model:
			self.setSourceModel(bin_columns_model)
			

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		
		if not self.isEnabled():
			return True
		
		is_hidden = self.sourceModel().index(source_row, 0, source_parent).data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
		
		return not is_hidden
	
	def setEnabled(self, is_enabled:bool):
		
		if self._is_enabled == is_enabled:
			return
		
		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)