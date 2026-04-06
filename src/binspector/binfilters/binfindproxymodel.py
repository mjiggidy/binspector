from PySide6 import QtCore
from . import abstractfiltermodel

class BSFindInBinProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):
	"""Find In Bin - Search bin column for text"""

	sig_search_text_changed  = QtCore.Signal(str)
	sig_case_sensive_enabled = QtCore.Signal(bool)

	def __init__(self, *args, search_text:str="", case_sensitive:bool=False, **kwargs):

		super().__init__(*args, **kwargs)

		self._search_text    = search_text
		self._case_sensitive = case_sensitive

	@QtCore.Slot(str)
	def setSearchText(self, search_text:str):

		if self._search_text == search_text:
			return
		
		self.beginFilterChange()
		self._search_text = search_text
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

		self.sig_search_text_changed.emit(search_text)

	def searchText(self) -> str:

		return self._search_text

	def setEnabled(self, is_enabled):
		
		if self._is_enabled == is_enabled:
			return
		
		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)

	@QtCore.Slot(bool)
	def setCaseSensitive(self, is_case_sensitive:bool):

		if self._case_sensitive == is_case_sensitive:
			return
		
		self.beginFilterChange()
		self._case_sensitive = is_case_sensitive
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

		self.sig_case_sensive_enabled.emit(is_case_sensitive)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex):
		
		if not self._is_enabled or not self._search_text:
			return True
		
		if not self._search_text:
			return True
		
		
		search_text = self._search_text if self._case_sensitive else self._search_text.casefold()
		
		# Build search text from visible columns
		for source_col_idx in range(self.columnCount(QtCore.QModelIndex())):

			src_index           = self.sourceModel().index(source_row, source_col_idx, source_parent)
			src_filter_data:str = src_index.data(QtCore.Qt.ItemDataRole.DisplayRole) # PRESUMPTUOUS!

			if src_filter_data and search_text in (src_filter_data if self._case_sensitive else src_filter_data.casefold()):
				return True

		return False