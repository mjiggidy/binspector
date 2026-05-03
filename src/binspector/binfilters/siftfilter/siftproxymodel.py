import typing
from PySide6 import QtCore

from .  import sifters
from .. import abstractfiltermodel

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	def __init__(self, *args, sift_criteria:typing.Iterable[sifters.BSAbstractSifter]|None=None, **kwargs):

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
	def setSiftCriteria(self, criteria:typing.Tuple[list[sifters.BSAbstractSifter],list[sifters.BSAbstractSifter]]):

		# NOTE: Just for now using crit 1
		# Will want to convert this in like the widget or something instead

		self.beginFilterChange()

		crit1, crit2 = criteria

		self._sift_criteria = crit1
		
#		self._sift_criteria = list(criteria_1)
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self.isEnabled():
			return True
		
		if source_parent.isValid():
			return False
		
		source_index = self.sourceModel().index(source_row, 0, QtCore.QModelIndex())



		return all(crit.scope_accepts_index(source_index) for crit in self._sift_criteria)