from . import columnsmodel

from PySide6 import QtCore, QtWidgets
from avbutils import bins

class SiftOptionWidget(QtWidgets.QWidget):
	"""A single sift option widget"""

	sig_option_set                    = QtCore.Signal()
	sig_columns_chooser_model_changed = QtCore.Signal(QtCore.QAbstractItemModel)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))

		self._cmb_match_method = QtWidgets.QComboBox()
		self._txt_match_text   = QtWidgets.QLineEdit()
		self._cmb_match_column = QtWidgets.QComboBox()

		self._default_sift_option = bins.BinSiftOption(bins.BinSiftMethod.CONTAINS, "", "Any")

		self.layout().addWidget(self._cmb_match_method,  0, 0)
		self.layout().addWidget(self._txt_match_text,  0, 1)
		self.layout().addWidget(self._cmb_match_column, 0, 2)

		self._setupWidgets()
		self._setupSignals()

	def _setupWidgets(self):

		for sift_method in bins.BinSiftMethod:
			self._cmb_match_method.addItem(sift_method.name.replace("_"," ").title() + ":", sift_method)

		#for column_name, column_index in bins.BIN_COLUMN_ROLES.items():
		#	#(column_name, column_index)
		#	self._cmb_match_column.addItem(column_name, column_index)

		self._cmb_match_column.setMinimumContentsLength(12)
		self._cmb_match_column.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

	def _setupSignals(self):

		self._cmb_match_column.activated.connect(self.sig_option_set)
		self._cmb_match_method.activated.connect(self.sig_option_set)
		self._txt_match_text.editingFinished.connect(self.sig_option_set)

	@QtCore.Slot(object)
	def setSiftOption(self, sift_option:bins.BinSiftOption):

		sift_option = sift_option or self._default_sift_option

		self._cmb_match_method.setCurrentIndex(self._cmb_match_method.findData(sift_option.sift_method))
		self._txt_match_text.setText(sift_option.sift_text)
		self._cmb_match_column.setCurrentText(sift_option.sift_column or "None")

		#print(sift_option)

		#self.sig_option_set.emit()

	def siftOption(self) -> bins.BinSiftOption:

		return bins.BinSiftOption(
			sift_method = self._cmb_match_method.currentData(),
			sift_text   = self._txt_match_text.text(),
			sift_column = self._cmb_match_column.currentText()
		)

	@QtCore.Slot(list)
	def setColumnsChooserModel(self, columns_chooser_model:columnsmodel.BSBinSiftColumnChooserModel):

		if self._cmb_match_column.model() == columns_chooser_model:
			return

		self._cmb_match_column.setModel(columns_chooser_model)

		self.sig_columns_chooser_model_changed.emit(columns_chooser_model)