import logging, typing
from PySide6 import QtCore

from .  import sifters
from .. import abstractfiltermodel
from ...binview import binviewitemtypes

import avbutils

SiftCriteria:typing.TypeAlias = list[list[sifters.BSAbstractSifter]]
"""A list lists of `and` criteria, each to be compared with `or`"""

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	DEFAULT_CRITERIA:SiftCriteria = [[sifters.BSAnyColumnSifter()]*3]*2

	sig_live_sift_enabled = QtCore.Signal(bool)
	"""Live Sift was toggled on or off"""

	sig_criteria_changed  = QtCore.Signal(object)
	"""Sift criteria was changed"""

	def __init__(self, *args, sift_criteria:SiftCriteria|None=None, live_sift:bool=False, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._sift_criteria = sift_criteria or list(self.DEFAULT_CRITERIA)

		# NOTE to self:  Live Sift does two things:
		# - Toggle dynamic filter here in the proxy so it responds to changes in data
		# - Toggle if sig_criteria_set is emitted by the widget on every change, or when the 
		#   user clicks a button to re-sift
		
		self.setDynamicSortFilter(live_sift)

	def setSourceModel(self, source_model:QtCore.QAbstractItemModel):
		
		if self.sourceModel() == source_model:
			return
		
		if self.sourceModel():
			self.sourceModel().disconnect(self)

		source_model.columnsAboutToBeRemoved.connect(self.sourceColumnsAboutToBeRemoved)
		
		return super().setSourceModel(source_model)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceColumnsAboutToBeRemoved(self, source_parent:QtCore.QModelIndex, first:int, last:int):

		# Evaluate which columns will be removed, and set any related filters to 'None' to deactivate

		# Determine the column info about to be removed
		column_infos_to_be_removed:list[binviewitemtypes.BSBinViewColumnInfo] = []
		
		for col_idx in range(first, last+1):

			field_id_removing = self.sourceModel().headerData(
				col_idx,
				QtCore.Qt.Orientation.Horizontal,
				binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole
			)

			name_removing = self.sourceModel().headerData(
				col_idx,
				QtCore.Qt.Orientation.Horizontal,
				binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole
			)

			column_data = (field_id_removing, name_removing)
			column_infos_to_be_removed.append(column_data)

			logging.getLogger(__name__).debug("I hear we're removing: %s", name_removing)

		validated_sift_criteria:SiftCriteria = []

		for criterion_set in self._sift_criteria:

			validated_criterion_set = []

			for criterion in criterion_set:

				is_valid = True

				# Ensure this criterion does not reference a column in the removals list
#				logging.getLogger(__name__).debug("Looking at %s...", criterion)

				if isinstance(criterion, sifters.BSSingleColumnSifter):

					if criterion.siftColumnInfo().field_id == avbutils.bins.BinColumnFieldIDs.User:
						is_valid = (criterion.siftColumnInfo().field_id, criterion.siftColumnInfo().display_name) not in column_infos_to_be_removed
					
					else:
						is_valid = criterion.siftColumnInfo().field_id not in map(lambda i: i[0], column_infos_to_be_removed)

				elif isinstance(criterion, sifters.BSRangeSifter):
					
					for range_field_id, info in sifters.rangesifter.SIFT_RANGE_COLUMN_DEPENDENCIES.items():
						
						if info.range_role == criterion.dataRole():
							is_valid = range_field_id not in map(lambda i: i[0], column_infos_to_be_removed)
							break

				# Either pass through the existing criterion, or set to NoColumn if the column gon b goin byebye night night.

				if is_valid:

					logging.getLogger(__name__).debug("Sift passes: %s", repr(criterion))
					validated_criterion_set.append(criterion)
				
				else:
					
					modified_criterion = sifters.BSNoColumnSifter(
							sift_string = criterion.siftString(),
							match_type  = criterion.matchType(),
						)

					logging.getLogger(__name__).debug("Sift to be reset:", repr(modified_criterion))

					validated_criterion_set.append(modified_criterion)

			validated_sift_criteria.append(validated_criterion_set)
		
		self.setSiftCriteria(validated_sift_criteria)

	###

	@QtCore.Slot()
	def resetSiftCriteria(self):
		"""Reset sift criteria to defaults"""
		
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
	def setSiftCriteria(self, criteria:SiftCriteria):

		if not criteria:
			criteria = list(self.DEFAULT_CRITERIA)

		if self._sift_criteria == criteria:

			logging.getLogger(__name__).debug("Sift critera unchanged")
			return

		self.beginFilterChange()
		self._sift_criteria = criteria
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		logging.getLogger(__name__).debug("Sift criteria changed (%s)", self._sift_criteria)

		self.sig_criteria_changed.emit(self._sift_criteria)

	def siftCriteria(self) -> SiftCriteria:

		return self._sift_criteria
	
	@QtCore.Slot(bool)
	def setLiveSiftEnabled(self, is_enabled:bool):

		if self.dynamicSortFilter() == is_enabled:
			return
		
		self.setDynamicSortFilter(is_enabled)

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

				accepted = criteria.sifterAcceptsIndex(source_index)

				local_results.append(accepted)

				if not accepted: # ngmi
					break
			
			if local_results:
				
				if all(local_results): # We got em, fellas.
					return True

				sift_results.append(all(local_results))

		return any(sift_results) if sift_results else True