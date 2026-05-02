import typing
from PySide6 import QtCore

from .  import scope
from .. import abstractfiltermodel
import avbutils

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	def __init__(self, *args, sift_criteria:typing.Iterable|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._sift_criteria = list(sift_criteria) if sift_criteria is not None else []

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):

		if self._is_enabled == is_enabled:
			return

		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)
	
	@QtCore.Slot(object)
	def setSiftCriteria(self, sift_criteria:typing.Iterable):

		if self._sift_criteria == sift_criteria:
			return

		self.beginFilterChange()
		self._sift_criteria = list(sift_criteria)
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self.isEnabled():
			return True
		
		if source_parent.isValid():
			return False
		
		source_index = self.sourceModel().index(source_row, 0, QtCore.QModelIndex())

		return all(crit.option_accepts_row(source_index) for crit in self._sift_criteria)