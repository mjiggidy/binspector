"""
Widgets for sifting bin contents
"""

import typing, logging

from PySide6 import QtCore, QtWidgets
from avbutils import bins

from . import scopesmodel

from .siftcriteriawidget import BSSiftCriteriaWidget
from ..binfilters.siftfilter import sifters

class BSSiftSettingsWidget(QtWidgets.QWidget):
	
	CRITERIA_PER_SIFT           = 3
	DEFAULT_CRITERIA_TIMEOUT_MS = 200
	DEFAULT_SIFT_CRITERIA       = BSSiftCriteriaWidget.DEFAULT_SIFT_CRITERIA

	sig_criteria_set      = QtCore.Signal(object)
	sig_live_sift_enabled = QtCore.Signal(bool)

	def __init__(self, *args, bin_view_model:QtCore.QAbstractItemModel|None=None, live_sift:bool=False, **kwargs):

		super().__init__(*args, **kwargs)

		self._columns_chooser_model = scopesmodel.BSSiftScopeViewModel(bin_view_model=bin_view_model or QtCore.QIdentityProxyModel())

		self._live_sift_enabled = live_sift

		self.setLayout(QtWidgets.QVBoxLayout())

		self.setSizePolicy(
			QtWidgets.QSizePolicy.Policy.Preferred,
			QtWidgets.QSizePolicy.Policy.Fixed
		)

		self.grp_sift_top    = QtWidgets.QGroupBox()
		self.grp_sift_bottom = QtWidgets.QGroupBox()
	
		self._sift_top_widgets:list[BSSiftCriteriaWidget] = []
		self._sift_bot_widgets:list[BSSiftCriteriaWidget] = []
		
		self._criteria_changed_timer = QtCore.QTimer(parent=self, singleShot=True, interval=self.DEFAULT_CRITERIA_TIMEOUT_MS)
		
		self._chk_live_sift = QtWidgets.QCheckBox()

		self._btn_apply = QtWidgets.QPushButton()
		self._btn_clear = QtWidgets.QPushButton()

		for _ in range(self.CRITERIA_PER_SIFT):
			self._sift_top_widgets.append(BSSiftCriteriaWidget(sources_model=self._columns_chooser_model))

		for _ in range(self.CRITERIA_PER_SIFT):
			self._sift_bot_widgets.append(BSSiftCriteriaWidget(sources_model=self._columns_chooser_model))
		
		self._setupWidgets()
		self._setupSignals()
	
	def _setupWidgets(self):

		self.grp_sift_top.setLayout(QtWidgets.QVBoxLayout())
		self.grp_sift_top.setTitle(self.tr("Show clips that meet this criteria:"))

		self.grp_sift_bottom.setLayout(QtWidgets.QVBoxLayout())
		self.grp_sift_bottom.setTitle(self.tr("Or, show clips that meet this criteria:"))

		self.layout().addWidget(self.grp_sift_top)

		#self.grp_sift_top   .layout().setContentsMargins(2,2,2,2)
		self.grp_sift_top   .layout().setSpacing(2)
		
		#self.grp_sift_bottom.layout().setContentsMargins(2,2,2,2)
		self.grp_sift_bottom.layout().setSpacing(2)

		for wdg in self._sift_top_widgets:
			self.grp_sift_top.layout().addWidget(wdg)

		self.layout().addWidget(self.grp_sift_bottom)

		for wdg in self._sift_bot_widgets:
			self.grp_sift_bottom.layout().addWidget(wdg)

		self._chk_live_sift.setText(self.tr("Live Sift"))
		self._chk_live_sift.setChecked(self._live_sift_enabled)
		self._chk_live_sift.toggled.connect(self.setLiveSiftEnabled)
				
		self._btn_apply.setText(self.tr("Apply"))
		self._btn_apply.setDefault(True)
		self._btn_apply.setDisabled(self._live_sift_enabled)		

		self._btn_clear.setText(self.tr("Clear"))

		lay_buttons = QtWidgets.QHBoxLayout()
		lay_buttons.addWidget(self._chk_live_sift)
		lay_buttons.addStretch()
		lay_buttons.addWidget(self._btn_clear)
		lay_buttons.addWidget(self._btn_apply)

		self.layout().addLayout(lay_buttons)

	def _setupSignals(self):

		self._criteria_changed_timer.timeout.connect(self.criteriaSettled)
		self._btn_apply.clicked.connect(self.criteriaSettled)
		self._btn_clear.clicked.connect(self.resetAllCriteria)

		for wdg in self._sift_top_widgets:
			wdg.sig_criteria_set.connect(self.criteriaChanged)

		for wdg in self._sift_bot_widgets:
			wdg.sig_criteria_set.connect(self.criteriaChanged)

	@QtCore.Slot(bool)
	def setLiveSiftEnabled(self, is_enabled:bool):
		"""
		If Live Sift is enabled, `sig_criteria_set` will emit on live changes.\n
		Without Live Sift, `sig_criteria_set` will emit only when the user submits changes
		"""

		if self._live_sift_enabled == is_enabled:
			return
		
		logging.getLogger(__name__).debug(f"Live Sift set to %s", is_enabled)
		
		self._live_sift_enabled = is_enabled

		self._btn_apply.setDisabled(self._live_sift_enabled)

		self.sig_live_sift_enabled.emit(is_enabled)

	def liveSiftEnabled(self) -> bool:
		"""Is widget reporting changes as they happen"""

		return self._live_sift_enabled

	@QtCore.Slot(object)
	def setBinViewModel(self, bin_view_model:QtCore.QAbstractItemModel):
		"""Set the bin view model for the sources chooser"""

		self._columns_chooser_model.setBinViewModel(bin_view_model)
	
	@QtCore.Slot()
	def criteriaChanged(self):
		"""Sift criteria was changed"""

		if self._live_sift_enabled:
			self._criteria_changed_timer.start()

	@QtCore.Slot()
	def criteriaSettled(self):
		"""Sift criteria is final"""

		self.sig_criteria_set.emit(self.criteria())

	def criteria(self) -> typing.Tuple[list[sifters.BSAbstractSifter],list[sifters.BSAbstractSifter]]:
		"""The sift criteria as currently set"""

		return (
			[s.criteria() for s in self._sift_top_widgets],
			[s.criteria() for s in self._sift_bot_widgets]
		)
	
	@QtCore.Slot()
	def resetAllCriteria(self):

		self.setCriteria(
			(
				[self.DEFAULT_SIFT_CRITERIA]*self.CRITERIA_PER_SIFT,
				[self.DEFAULT_SIFT_CRITERIA]*self.CRITERIA_PER_SIFT,
			)
		)

	@QtCore.Slot(object)
	def setCriteria(self, criteria:typing.Tuple[list[sifters.BSAbstractSifter],list[sifters.BSAbstractSifter]]):

		# TODO: Think about this when I'm having a "good" day

		if len(criteria) != 2:
			raise ValueError("Exactly two sets of criteria must be provided")
		
		self.setTopCriteria(criteria[0])
		self.setBottomCriteria(criteria[1])

	@QtCore.Slot(object)
	def setTopCriteria(self, criteria:list[sifters.BSAbstractSifter]):

#		print("--- SET TOP")
#		for c in criteria:
#			print(c)

		self._setSectionCriteria(self._sift_top_widgets, criteria=criteria)

	@QtCore.Slot(object)
	def setBottomCriteria(self, criteria:list[sifters.BSAbstractSifter]):

#		print("--- SET BOTTOM")
#		for c in criteria:
#			print(c)

		self._setSectionCriteria(self._sift_bot_widgets, criteria=criteria)

	def _setSectionCriteria(self, widget_list:list[BSSiftCriteriaWidget], criteria:list[sifters.BSAbstractSifter]):

		if len(criteria) != len(widget_list):
			raise ValueError(f"A set of exactly {len(widget_list)} criteria must be provided (got {criteria})")
		
		for widget, criteria in zip(widget_list, criteria):
			widget.setCriteria(criteria)