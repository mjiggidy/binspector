import typing

from . import sourcesmodel

from PySide6 import QtCore, QtWidgets
from avbutils import bins

class SiftOptionWidget(QtWidgets.QWidget):
	"""A single sift option widget"""

	sig_option_set                    = QtCore.Signal(object)
	sig_columns_chooser_model_changed = QtCore.Signal(QtCore.QAbstractItemModel)

	DEFAULT_OPTION_CHANGED_TIMEOUT_MSEC = 500

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))

		self._txt_match_text   = QtWidgets.QLineEdit()
		self._cmb_match_method = QtWidgets.QComboBox()
		self._cmb_match_column = QtWidgets.QComboBox()

		self._default_sift_option = bins.BinSiftOption(bins.BinSiftMethod.CONTAINS, "", "Any")

		self._option_changed_timer = QtCore.QTimer(parent=self, singleShot=True, interval=self.DEFAULT_OPTION_CHANGED_TIMEOUT_MSEC)

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

		self._txt_match_text.textChanged    .connect(self.siftTextSet)
		self._cmb_match_method.activated    .connect(self.siftMethodChosen)
		self._cmb_match_column.activated    .connect(self.siftSourceChosen)

		self._option_changed_timer.timeout  .connect(self.siftOptionSettled)

	@QtCore.Slot()
	def siftOptionSettled(self):

		self.sig_option_set.emit(self.siftOption())
		print(self.siftOption())

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
			sift_method = self.siftMethod(),
			sift_text   = self._txt_match_text.text(),
			sift_column = self.siftSource()
		)

	@QtCore.Slot(list)
	def setColumnsChooserModel(self, columns_chooser_model:sourcesmodel.BSSiftSourcesViewModel):

		if self._cmb_match_column.model() == columns_chooser_model:
			return

		self._cmb_match_column.setModel(columns_chooser_model)

		self.sig_columns_chooser_model_changed.emit(columns_chooser_model)

	def setSiftMethod(self, sift_method:bins.BinSiftMethod.CONTAINS):

		if self._cmb_match_method.currentData() == sift_method:
			return
			
		idx_method = self._cmb_match_method.findData(sift_method)
		self._cmb_match_method.setCurrentIndex(idx_method)

	def siftMethod(self) -> bins.BinSiftMethod:
		return self._cmb_match_method.currentData()
	
	@QtCore.Slot()
	def siftTextSet(self):

		self._option_changed_timer.start()

	@QtCore.Slot()
	def siftSourceChosen(self):

		sift_source_type, _ = self._cmb_match_column.currentData()
		
		if sift_source_type == sourcesmodel.BSSiftSourceType.Range:
			self.setSiftMethod(bins.BinSiftMethod.CONTAINS)

		self._option_changed_timer.start()

	def siftSource(self) -> typing.Tuple[sourcesmodel.BSSiftSourceType, typing.Any]:

		return self._cmb_match_column.currentData()

	@QtCore.Slot()
	def siftMethodChosen(self):

		sift_method = self._cmb_match_method.currentData()
		
		if sift_method != bins.BinSiftMethod.CONTAINS:

			sift_source_type, _ = self.siftSource()
			
			if sift_source_type == sourcesmodel.BSSiftSourceType.Range:

				self.setSiftSource(source_type=sourcesmodel.BSSiftSourceType.AnyColumn)

		self._option_changed_timer.start()

	def setSiftSource(self, source_type:sourcesmodel.BSSiftSourceType):

		if not source_type == sourcesmodel.BSSiftSourceType.AnyColumn:
			raise NotImplementedError("Nope")
		
		self._cmb_match_column.setCurrentIndex(0)

		self._option_changed_timer.start()