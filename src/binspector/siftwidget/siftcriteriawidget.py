import typing

from PySide6 import QtCore, QtWidgets

import binspector.binfilters.siftfilter.siftscopetypes

from . import scopesmodel
from ..binfilters.siftfilter import sifters, siftmatchtypes

import avbutils


class BSSiftCriteriaWidget(QtWidgets.QWidget):
	"""A single sift option widget"""

	sig_criteria_set        = QtCore.Signal(object)
	sig_scope_model_changed = QtCore.Signal(QtCore.QAbstractItemModel)
	sig_scope_changed       = QtCore.Signal(object)
	sig_match_type_changed  = QtCore.Signal(object)
	sig_text_changed        = QtCore.Signal(str)

	DEFAULT_SIFT_CRITERIA               = sifters.BSAnyColumnSifter(sift_string="", match_type=siftmatchtypes.BSSiftMatchTypes.Contains)
	CRITERIA_CHANGED_TIMEOUT_MSEC       = 200

	def __init__(self, *args, sources_model:scopesmodel.BSSiftScopeViewModel, sift_criteria:sifters.BSAbstractSifter|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))
		self.layout().setSpacing(2)

		self._txt_match_text  = QtWidgets.QLineEdit()
		self._cmb_match_type  = QtWidgets.QComboBox()
		self._cmb_match_scope = QtWidgets.QComboBox(model=sources_model)

		self._criteria_changed_timer = QtCore.QTimer(parent=self, singleShot=True, interval=self.CRITERIA_CHANGED_TIMEOUT_MSEC)

		self._setupWidgets()
		self._setupSignals()

		if sift_criteria:
			self.setCriteria(sift_criteria)

	def _setupWidgets(self):

		self._cmb_match_scope.setMinimumContentsLength(12)
		self._cmb_match_scope.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

		# Set up Match Type list items
		self._cmb_match_type.addItem(self.tr("Contains:"),        siftmatchtypes.BSSiftMatchTypes.Contains)
		self._cmb_match_type.addItem(self.tr("Begins With:"),     siftmatchtypes.BSSiftMatchTypes.BeginsWith)
		self._cmb_match_type.addItem(self.tr("Matches Exactly:"), siftmatchtypes.BSSiftMatchTypes.MatchesExactly)

		self.layout().addWidget(self._cmb_match_type,  0, 0)
		self.layout().addWidget(self._txt_match_text,  0, 1)
		self.layout().addWidget(self._cmb_match_scope, 0, 2)

	def _setupSignals(self):

		self._txt_match_text.textChanged     .connect(self.textChosen)
		self._cmb_match_type.activated       .connect(self.matchTypeChosen)
		self._cmb_match_scope.activated      .connect(self.scopeChosen)

		self._criteria_changed_timer.timeout .connect(self.criteriaSettled)

	@QtCore.Slot()
	def criteriaSettled(self):
		"""Sift criteria have survived the timer, emit it"""

		self.sig_criteria_set.emit(self.criteria())

	@QtCore.Slot(object)
	def setCriteria(self, sift_criteria:sifters.BSAbstractSifter):
		"""Set the sift criteria for this widget"""

		if self.criteria() == sift_criteria:
			return

		sift_criteria = sift_criteria or self.DEFAULT_SIFT_CRITERIA

		self._cmb_match_type.setCurrentIndex(self._cmb_match_type.findData(sift_criteria.matchType()))
		self._txt_match_text.setText(sift_criteria.siftString())
		
		scope_model:scopesmodel.BSSiftScopeViewModel = self._cmb_match_scope.model()
		
		if isinstance(sift_criteria, sifters.BSSingleColumnSifter):

#			print(f"Look for ", sift_criteria.siftColumnInfo(), "in ", sift_criteria.siftColumnInfo())
#			print(f"** Found: ", self._cmb_match_scope.findData(sift_criteria.siftColumnInfo()))
			
			ranges_available  = scope_model.rowCountForScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.SingleColumn)

			if not ranges_available:
				raise ValueError("No column names available")
			
			ranges_offset = scope_model.rowOffsetToScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.SingleColumn)

			cmb_idx = None
			
			for row in range(ranges_offset, ranges_available + ranges_offset):

				_, range_role = self._cmb_match_scope.itemData(row)

				if sift_criteria.siftColumnInfo().field_id == range_role.field_id:
				
					# User columns need to be matched by name as well
					if sift_criteria.siftColumnInfo().field_id == avbutils.bins.BinColumnFieldIDs.User \
						and sift_criteria.siftColumnInfo().display_name != range_role.display_name:
							continue

					cmb_idx = row
					break

			if cmb_idx is None:
				raise ValueError("Nope")

			self._cmb_match_scope.setCurrentIndex(cmb_idx)

		elif isinstance(sift_criteria, sifters.BSAnyColumnSifter):

			self._cmb_match_scope.setCurrentIndex(
				scope_model.rowOffsetToScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.AnyColumn)
			)

		elif isinstance(sift_criteria, sifters.BSNoColumnSifter):

			self._cmb_match_scope.setCurrentIndex(
				scope_model.rowOffsetToScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.NoColumn)
			)

		elif isinstance(sift_criteria, sifters.BSRangeSifter):

			ranges_available  = scope_model.rowCountForScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.Range)

			if not ranges_available:
				raise ValueError("No column names available")
			
			ranges_offset = scope_model.rowOffsetToScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.Range)

			cmb_idx = None
			
			for row in range(ranges_offset, ranges_available + ranges_offset):

				_, range_role = self._cmb_match_scope.itemData(row)

				if sift_criteria.dataRole() == range_role:
				
					cmb_idx = row
					break

			if cmb_idx is None:
				raise ValueError("Nope")

			self._cmb_match_scope.setCurrentIndex(cmb_idx)

		else:
			raise ValueError(f"Unknown sifter round here: {sift_criteria}")

		self.sig_criteria_set.emit(sift_criteria)

	def criteria(self) -> sifters.BSAbstractSifter:
		"""Build a `BSAbstractSifter` based on current user input"""

		source_type, source_id = self.siftSource()

		if source_type == binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.SingleColumn:

			return sifters.BSSingleColumnSifter(
				sift_column_info = source_id,
				sift_string      = self.text(),
				match_type       = self.matchType(),
			)
		
		elif source_type == binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.AnyColumn:

			return sifters.BSAnyColumnSifter(
				sift_string = self.text(),
				match_type  = self.matchType(),
			)

		elif source_type == binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.NoColumn:

			return sifters.BSNoColumnSifter(
				sift_string= self.text(),
				match_type = self.matchType(),
			)
		
		elif source_type == binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.Range:

			return sifters.BSRangeSifter(
				sift_string = self.text(),
				data_role   = source_id,
			)
		
		else:
			raise ValueError("Nuh uh")

	@QtCore.Slot(list)
	def setScopeChooserModel(self, scope_chooser_model:scopesmodel.BSSiftScopeViewModel):
		"""Set the scope chooser model"""

		if self._cmb_match_scope.model() == scope_chooser_model:
			return

		self._cmb_match_scope.setModel(scope_chooser_model)

		self.sig_scope_model_changed.emit(scope_chooser_model)

	def scopeChooserModel(self) -> scopesmodel.BSSiftScopeViewModel:
		"""The scope chooser model"""

		return self._cmb_match_scope.model()

	def setMatchType(self, match_type:binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType):
		"""Set the string matching strategy to use during the sift"""

		if self._cmb_match_type.currentData() == match_type:
			return
			
		self._cmb_match_type.setCurrentIndex(
			self._cmb_match_type.findData(match_type)
		)

		self.sig_match_type_changed.emit(match_type)

	def matchType(self) -> siftmatchtypes.BSSiftMatchTypes:
		"""The string matching strategy to use during the sift"""

		return self._cmb_match_type.currentData()
	
	@QtCore.Slot(str)
	def setText(self, sift_text:str) -> str:
		"""Set the text for which to sift"""

		if self._txt_match_text.text() == sift_text:
			return

		self._txt_match_text.setText(sift_text)

		self.sig_text_changed.emit(sift_text)
	
	def text(self) -> str:
		"""The text for which to sift"""

		return self._txt_match_text.text()

	def siftSource(self) -> typing.Tuple[binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType, typing.Any]:

		return self._cmb_match_scope.currentData()

	def scope(self) -> binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType:
		"""Which scope to sift -- such as a particular column, a particular range, etc."""

		return self._cmb_match_scope.currentData()
	
	@QtCore.Slot()
	def textChosen(self):
		"""User typed something"""

		self._criteria_changed_timer.start()

	@QtCore.Slot()
	def scopeChosen(self):
		"""User set the scope"""

		sift_source_type, _ = self._cmb_match_scope.currentData()
		
		if sift_source_type == binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.Range:
			self.setMatchType(siftmatchtypes.BSSiftMatchTypes.Contains)

		self._criteria_changed_timer.start()

	@QtCore.Slot()
	def matchTypeChosen(self):
		"""User set the sift match type"""

		sift_method = self._cmb_match_type.currentData()
		
		if sift_method != siftmatchtypes.BSSiftMatchTypes.Contains:

			sift_source_type, _ = self.siftSource()
			
			if sift_source_type == binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.Range:
				self._cmb_match_scope.setCurrentIndex(
					self._cmb_match_scope.model().rowOffsetToScope(binspector.binfilters.siftfilter.siftscopetypes.BSSiftScopeType.AnyColumn)
				)

		self._criteria_changed_timer.start()