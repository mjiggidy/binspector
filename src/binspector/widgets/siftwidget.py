"""
Widgets for sifting bin contents
"""

from PySide6 import QtCore, QtGui, QtWidgets
from avbutils import bins

class BSSiftOptionWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))

		self._cmb_match_method = QtWidgets.QComboBox()
		self._txt_match_text   = QtWidgets.QLineEdit()
		self._cmb_match_column = QtWidgets.QComboBox()

		self.layout().addWidget(self._cmb_match_method,  0, 0)
		self.layout().addWidget(self._txt_match_text,  0, 1)
		self.layout().addWidget(self._cmb_match_column, 0, 2)

		self._setupWidgets()

	def _setupWidgets(self):

		for sift_method in bins.BinSiftMethod:
			self._cmb_match_method.addItem(sift_method.name.replace("_"," ").title() + ":", sift_method.value)
		
		for column_name, column_index in bins.BIN_COLUMN_ROLES.items():
			print(column_name, column_index)
			self._cmb_match_column.addItem(column_name, column_index)
		
		self._cmb_match_column.setMinimumContentsLength(12)
		self._cmb_match_column.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
	
	def setSiftOption(self, sift_method:bins.BinSiftMethod, sift_string:str, sift_column:str):

		self._cmb_match_method.setCurrentIndex(sift_method.value)
		self._txt_match_text.setText(sift_string)
		self._cmb_match_method.setCurrentText(sift_column)

class BSSiftSettingsWidget(QtWidgets.QWidget):

	CRITERIA_PER_SIFT = 3

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

		self.btn_dialog.setStandardButtons(
			QtWidgets.QDialogButtonBox.StandardButton.Apply|QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Reset
		)
		self.btn_dialog.button(QtWidgets.QDialogButtonBox.StandardButton.Reset).setText(self.tr("Clear"))

		self.layout().addWidget(self.grp_sift_top)

		for idx in range(self.CRITERIA_PER_SIFT):
			self.grp_sift_top.layout().addWidget(BSSiftOptionWidget())

		self.layout().addWidget(self.grp_sift_bottom)

		for idx in range(self.CRITERIA_PER_SIFT):
			self.grp_sift_bottom.layout().addWidget(BSSiftOptionWidget())

		self.layout().addWidget(self.btn_dialog)