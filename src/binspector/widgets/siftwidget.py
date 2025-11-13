"""
Widgets for sifting bin contents
"""

import dataclasses
import avb
from PySide6 import QtCore, QtGui, QtWidgets
from avbutils import bins

@dataclasses.dataclass(frozen=True)
class BSSiftOption:

	sift_method:bins.BinSiftMethod
	sift_text  :str
	sift_column:str

class BSSiftOptionWidget(QtWidgets.QWidget):
	
	sig_option_set = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))

		self._cmb_match_method = QtWidgets.QComboBox()
		self._txt_match_text   = QtWidgets.QLineEdit()
		self._cmb_match_column = QtWidgets.QComboBox()

		self._default_sift_option = BSSiftOption(bins.BinSiftMethod.CONTAINS, "", "Any")

		self.layout().addWidget(self._cmb_match_method,  0, 0)
		self.layout().addWidget(self._txt_match_text,  0, 1)
		self.layout().addWidget(self._cmb_match_column, 0, 2)

		self._setupWidgets()

	def _setupWidgets(self):

		for sift_method in bins.BinSiftMethod:
			self._cmb_match_method.addItem(sift_method.name.replace("_"," ").title() + ":", sift_method)
		
		for column_name, column_index in bins.BIN_COLUMN_ROLES.items():
			#(column_name, column_index)
			self._cmb_match_column.addItem(column_name, column_index)
		
		self._cmb_match_column.setMinimumContentsLength(12)
		self._cmb_match_column.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
	
	@QtCore.Slot(object)
	def setSiftOption(self, sift_option:BSSiftOption):

		sift_option = sift_option or self._default_sift_option

		self._cmb_match_method.setCurrentIndex(self._cmb_match_method.findData(sift_option.sift_method))
		self._txt_match_text.setText(sift_option.sift_text)
		self._cmb_match_column.setCurrentText(sift_option.sift_column)

		self.sig_option_set.emit(sift_option)
	
	def siftOption(self) -> BSSiftOption:

		return BSSiftOption(
			sift_method = self._cmb_match_method.currentData(),
			sift_text   = self._txt_match_text.text(),
			sift_column = self._cmb_match_column.currentText()
		)
	
	@QtCore.Slot(list)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):
		
		self._cmb_match_column.clear()

		self._cmb_match_column.addItem("Any",None)
		self._cmb_match_column.insertSeparator(1)

		for bin_column in bin_view.columns:
			self._cmb_match_column.addItem(bin_column.get("title",""), bin_column.get("type"))
		

class BSSiftSettingsWidget(QtWidgets.QWidget):
	
	CRITERIA_PER_SIFT = 3

	sig_options_set = QtCore.Signal(list)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self.grp_sift_top    = QtWidgets.QGroupBox()
		self.grp_sift_bottom = QtWidgets.QGroupBox()
		self.btn_dialog      = QtWidgets.QDialogButtonBox()
		
		self.grp_sift_top.setLayout(QtWidgets.QVBoxLayout())
		self.grp_sift_top.setTitle(self.tr("Show clips that meet this criteria:"))

		self.grp_sift_bottom.setLayout(QtWidgets.QVBoxLayout())
		self.grp_sift_bottom.setTitle(self.tr("Or, show clips that meet this criteria:"))

		self._sift_top_widgets:list[BSSiftOptionWidget] = []
		self._sift_bot_widgets:list[BSSiftOptionWidget] = []

		self.btn_dialog.setStandardButtons(
			QtWidgets.QDialogButtonBox.StandardButton.Apply|QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Reset
		)
		self.btn_dialog.button(QtWidgets.QDialogButtonBox.StandardButton.Reset).setText(self.tr("Clear"))

		self.layout().addWidget(self.grp_sift_top)

		for _ in range(self.CRITERIA_PER_SIFT):
			wdg = BSSiftOptionWidget()
			self._sift_top_widgets.append(wdg)
			self.grp_sift_top.layout().addWidget(wdg)

		self.layout().addWidget(self.grp_sift_bottom)

		for _ in range(self.CRITERIA_PER_SIFT):
			wdg = BSSiftOptionWidget()
			self._sift_bot_widgets.append(wdg)
			self.grp_sift_bottom.layout().addWidget(wdg)

		self.layout().addWidget(self.btn_dialog)
	
	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):

		for wdg in self._sift_top_widgets:
			wdg.setBinView(bin_view)

		for wdg in self._sift_bot_widgets:
			wdg.setBinView(bin_view)
	
	@QtCore.Slot(list)
	def setSiftOptions(self, sift_options:list[BSSiftOption]):

		sift_options += [None] * max(0, (self.CRITERIA_PER_SIFT*2) - len(sift_options))

		for sift_widget, sift_option in zip(self._sift_top_widgets, sift_options[0:3]):
			sift_widget.setSiftOption(sift_option)

		for sift_widget, sift_option in zip(self._sift_bot_widgets, sift_options[3:6]):
			sift_widget.setSiftOption(sift_option)
		
		self.sig_options_set.emit(self.siftOptions())

	
	def siftOptions(self) -> list[BSSiftOption]:

		options = []

		options.extend([s.siftOption() for s in self._sift_top_widgets])
		options.extend([s.siftOption() for s in self._sift_bot_widgets])

		return options