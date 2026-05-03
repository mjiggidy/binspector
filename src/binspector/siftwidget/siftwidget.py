"""
Widgets for sifting bin contents
"""

import typing

from PySide6 import QtCore, QtWidgets
from avbutils import bins

from . import sourcesmodel

from .siftcriteriawidget import BSSiftCriteriaWidget
from ..binfilters.siftfilter import sifters

class BSSiftSettingsWidget(QtWidgets.QWidget):
	
	CRITERIA_PER_SIFT = 3
	DEFAULT_CRITERIA_TIMEOUT_MS = 200

	sig_criteria_set = QtCore.Signal(object)

	def __init__(self, *args, bin_view_model:QtCore.QAbstractItemModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._columns_chooser_model = sourcesmodel.BSSiftSourcesViewModel(bin_view_model=bin_view_model or QtCore.QIdentityProxyModel())

		self.setLayout(QtWidgets.QVBoxLayout())

		self.setSizePolicy(
			QtWidgets.QSizePolicy.Policy.Preferred,
			QtWidgets.QSizePolicy.Policy.Fixed
		)

		self.grp_sift_top    = QtWidgets.QGroupBox()
		self.grp_sift_bottom = QtWidgets.QGroupBox()
		#self.btn_dialog      = QtWidgets.QDialogButtonBox()
		
		self.grp_sift_top.setLayout(QtWidgets.QVBoxLayout())
		self.grp_sift_top.setTitle(self.tr("Show clips that meet this criteria:"))

		self.grp_sift_bottom.setLayout(QtWidgets.QVBoxLayout())
		self.grp_sift_bottom.setTitle(self.tr("Or, show clips that meet this criteria:"))

#		self._chk_enable_sift = QtWidgets.QCheckBox()

		self._sift_top_widgets:list[BSSiftCriteriaWidget] = []
		self._sift_bot_widgets:list[BSSiftCriteriaWidget] = []

		self._criteria_changed_timer = QtCore.QTimer(parent=self, singleShot=True, interval=self.DEFAULT_CRITERIA_TIMEOUT_MS)
		self._criteria_changed_timer.timeout.connect(self.siftCriteriaSettled)

#		self.btn_dialog.setStandardButtons(
#			QtWidgets.QDialogButtonBox.StandardButton.Apply|QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Reset
#		)
#		self.btn_dialog.button(QtWidgets.QDialogButtonBox.StandardButton.Reset).setText(self.tr("Clear"))

#		self._chk_enable_sift.setText("Enable Sift")
#		self._chk_enable_sift.toggled.connect(lambda: self.sig_options_set.emit(*self.siftCriteria()))
#		self.layout().addWidget(self._chk_enable_sift)
		
		self.layout().addWidget(self.grp_sift_top)

		#self.grp_sift_top   .layout().setContentsMargins(2,2,2,2)
		self.grp_sift_top   .layout().setSpacing(2)
		
		#self.grp_sift_bottom.layout().setContentsMargins(2,2,2,2)
		self.grp_sift_bottom.layout().setSpacing(2)


		for _ in range(self.CRITERIA_PER_SIFT):

			wdg = BSSiftCriteriaWidget()
			self._sift_top_widgets.append(wdg)

			wdg.setColumnsChooserModel(self._columns_chooser_model)
			
			wdg.sig_criteria_set.connect(self.siftCriteriaChanged)
			
			self.grp_sift_top.layout().addWidget(wdg)

		self.layout().addWidget(self.grp_sift_bottom)

		for _ in range(self.CRITERIA_PER_SIFT):
			
			wdg = BSSiftCriteriaWidget()
			self._sift_bot_widgets.append(wdg)
			
			wdg.setColumnsChooserModel(self._columns_chooser_model)
			
			wdg.sig_criteria_set.connect(self.siftCriteriaChanged)
			
			self.grp_sift_bottom.layout().addWidget(wdg)

		#self.layout().addWidget(self.btn_dialog)
	
	@QtCore.Slot(object)
	def setBinViewModel(self, bin_view_model:QtCore.QAbstractItemModel):

		self._columns_chooser_model.setBinViewModel(bin_view_model)

	
	@QtCore.Slot()
	def siftCriteriaChanged(self):

		self._criteria_changed_timer.start()

	@QtCore.Slot()
	def siftCriteriaSettled(self):

		self.sig_criteria_set.emit(self.siftCriteria())

	def siftCriteria(self) -> typing.Tuple[list[sifters.BSAbstractSifter],list[sifters.BSAbstractSifter]]:
		"""The sift criteria as currently set"""

		return (
			[s.siftCriteria() for s in self._sift_top_widgets],
			[s.siftCriteria() for s in self._sift_bot_widgets]
		)