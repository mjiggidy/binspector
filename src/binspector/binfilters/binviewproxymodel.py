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

	def moveRows(self, sourceParent:QtCore.QModelIndex, sourceRow:int, count:int, destinationParent:QtCore.QModelIndex, destinationChild:int) -> bool:

		if count > 1:
			# TODO
			raise NotImplementedError("TODO: Multiple row moves not yet implemented")
		
		if sourceParent.isValid() or destinationParent.isValid():
			return False
		
		mapped_source_idx      = self.mapToSource(self.index(sourceRow, 0, QtCore.QModelIndex())).row()
		mapped_destination_idx = self.mapToSource(self.index(destinationChild-1, 0, QtCore.QModelIndex())).row() + 1

		# NOTE ABOUT THE ABOVE: Want to move the visible column to JUST UNDER its left-neighboring visible column, so
		# getting the proxy index of the left neighbor, mapping it back to source (all columns), and adding one to put it after that
		# If destinationChild=0, I think that maps to invalid index -1, +1 = 0 so I think that's okay.
		
		return self.sourceModel().moveRows(
			QtCore.QModelIndex(),
			mapped_source_idx,
			count,
			QtCore.QModelIndex(),
			mapped_destination_idx
		)