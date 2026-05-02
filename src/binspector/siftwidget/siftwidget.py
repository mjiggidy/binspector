"""
Widgets for sifting bin contents
"""

from PySide6 import QtCore, QtWidgets
from avbutils import bins

from . import sourcesmodel

from .siftoptionwidget import SiftOptionWidget

class BSSiftSettingsWidget(QtWidgets.QWidget):
	
	CRITERIA_PER_SIFT = 3

	sig_options_set = QtCore.Signal(bool, object)

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

		self._chk_enable_sift = QtWidgets.QCheckBox()

		self._sift_top_widgets:list[SiftOptionWidget] = []
		self._sift_bot_widgets:list[SiftOptionWidget] = []

#		self.btn_dialog.setStandardButtons(
#			QtWidgets.QDialogButtonBox.StandardButton.Apply|QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Reset
#		)
#		self.btn_dialog.button(QtWidgets.QDialogButtonBox.StandardButton.Reset).setText(self.tr("Clear"))

		self._chk_enable_sift.setText("Enable Sift")
		self._chk_enable_sift.toggled.connect(lambda: self.sig_options_set.emit(*self.siftCriteria()))
#		self.layout().addWidget(self._chk_enable_sift)
		
		self.layout().addWidget(self.grp_sift_top)

		#self.grp_sift_top   .layout().setContentsMargins(2,2,2,2)
		self.grp_sift_top   .layout().setSpacing(2)
		
		#self.grp_sift_bottom.layout().setContentsMargins(2,2,2,2)
		self.grp_sift_bottom.layout().setSpacing(2)


		for _ in range(self.CRITERIA_PER_SIFT):
			wdg = SiftOptionWidget()
			wdg.setColumnsChooserModel(self._columns_chooser_model)
			wdg.sig_criteria_set.connect(lambda: self.sig_options_set.emit(*self.siftCriteria()))
			self._sift_top_widgets.append(wdg)
			self.grp_sift_top.layout().addWidget(wdg)

		self.layout().addWidget(self.grp_sift_bottom)

		for _ in range(self.CRITERIA_PER_SIFT):
			wdg = SiftOptionWidget()
			wdg.setColumnsChooserModel(self._columns_chooser_model)
			wdg.sig_criteria_set.connect(lambda: self.sig_options_set.emit(*self.siftCriteria()))
			self._sift_bot_widgets.append(wdg)
			self.grp_sift_bottom.layout().addWidget(wdg)

		#self.layout().addWidget(self.btn_dialog)
	
	@QtCore.Slot(object)
	def setBinViewModel(self, bin_view_model:QtCore.QAbstractItemModel):

		#print("HUH??")

		self._columns_chooser_model.setBinViewModel(bin_view_model)
	
	@QtCore.Slot(bool)
	def setSiftEnabled(self, is_enabled:bool):
		self._chk_enable_sift.setChecked(is_enabled)
	
#	@QtCore.Slot(list)
#	def setSiftOptions(self, sift_options:list[bins.BinSiftOption]|None=None):
#
#		#print("SIFT GOT", sift_options)
#
#		sift_options = sift_options or []
#
#		sift_options += [None] * max(0, (self.CRITERIA_PER_SIFT*2) - len(sift_options))
#
#		for sift_widget, sift_option in zip(self._sift_top_widgets, sift_options[0:3]):
#			sift_widget.setSiftOption(sift_option)
#
#		for sift_widget, sift_option in zip(self._sift_bot_widgets, sift_options[3:6]):
#			sift_widget.setSiftOption(sift_option)
#		
#		#self.sig_options_set.emit(*self.siftOptions())

	
	def siftCriteria(self) -> list[bins.BinSiftOption]:

		criteria = []

		criteria.extend([s.siftCriteria() for s in self._sift_top_widgets])
		criteria.extend([s.siftCriteria() for s in self._sift_bot_widgets])

		return (self._chk_enable_sift.isChecked(), criteria)