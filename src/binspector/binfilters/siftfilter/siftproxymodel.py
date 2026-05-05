import typing
from PySide6 import QtCore

from .  import sifters
from .. import abstractfiltermodel

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	DEFAULT_CRITERIA = [[sifters.BSAnyColumnSifter()]*3]*2

	sig_live_sift_enabled = QtCore.Signal(bool)
	"""Live Sift was toggled on or off"""

	sig_criteria_changed  = QtCore.Signal(object)
	"""Sift criteria was changed"""

	def __init__(self, *args, sift_criteria:list[list[sifters.BSAbstractSifter]]|None=None, live_sift:bool=False, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._sift_criteria = sift_criteria or list(self.DEFAULT_CRITERIA)

		# NOTE to self:  Live Sift does two things:
		# - Toggle dynamic filter here in the proxy so it responds to changes in data
		# - Toggle if sig_criteria_set is emitted by the widget on every change, or when the 
		#   user clicks a button to re-sift
		
		self.setDynamicSortFilter(live_sift)

	@QtCore.Slot()
	def resetSiftCriteria(self):

		self.setSiftCriteria(None)

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):

		# NOTE: isEnabled() implemented in base class

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

		if not criteria:
			criteria = list(self.DEFAULT_CRITERIA)

		if self._sift_criteria == criteria:
			return

		self.beginFilterChange()

		self._sift_criteria = criteria

		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

		self.sig_criteria_changed.emit(self._sift_criteria)

	def siftCriteria(self) -> list[list[sifters.BSAbstractSifter]]:

		return self._sift_criteria
	
	@QtCore.Slot(bool)
	def setLiveSiftEnabled(self, is_enabled:bool):

		if self.dynamicSortFilter() == is_enabled:
			return
		
		self.setDynamicSortFilter(True)
		self.invalidateRowsFilter()

		self.sig_live_sift_enabled.emit(is_enabled)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self.isEnabled():
			return True
		
		if not self._sift_criteria:
			return True
		
		source_index = self.sourceModel().index(source_row, 0, QtCore.QModelIndex())

		sift_results = []

		# TODO: Yeah, yeah.  I'll come back to this.
		# IT WORKS THOUGH DOESN'T IT?? HUH??  Or maybe it doesn't, 
		# if you're reading this.

		# Sift Criteria is a list of lists of "and" criterion
		# Each "and" list result is then compared with "or."
		# So "Match this, this, and this; or this, this, and this."
		
		# Criterion without a sift string set is considered invalid 
		# and neither True nor False.  Otherwise it janks up the sift 
		# boolean logic.

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