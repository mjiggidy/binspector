import typing
from PySide6 import QtCore

from .  import sifters
from .. import abstractfiltermodel

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	def __init__(self, *args, sift_criteria:list[list[sifters.BSAbstractSifter]]|None=None, live_sift:bool=True, **kwargs):

		super().__init__(*args, **kwargs)

		self._sift_criteria = sift_criteria if sift_criteria is not None else []

		# NOTE to self:  Live Sift does two things:
		# - Toggle dynamic filter here in the proxy so it responds to changes in data
		# - Toggle if sig_criteria_set is emitted by the widget on every change, or when the 
		#   user clicks a button to re-sift
		
		self.setDynamicSortFilter(live_sift)

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

		self._sift_criteria = [crit1, crit2]
		
#		self._sift_criteria = list(criteria_1)
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self.isEnabled():
			return True
		
		if not self._sift_criteria:
			return True
		
		source_index = self.sourceModel().index(source_row, 0, QtCore.QModelIndex())

		sift_results = []

		# TODO: Yeah, yeah.  I'll come back to this.  IT WORKS THOUGH DOESN'T IT?? HUH??

		for criteria_set in self._sift_criteria:

			local_results = []
			
			for criteria in criteria_set:

				# Invalid filters can be neither True nor False soooo
				if not criteria.isValid():
					continue

				local_results.append(criteria.sifterAcceptsIndex(source_index))
			
			if local_results:
				sift_results.append(all(local_results))

		return any(sift_results) if sift_results else True