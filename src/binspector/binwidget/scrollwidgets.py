"""
Widgets for adding as scrollBarWidgets to `QScrollArea`

Mostly standard widgets sublcassed for style
"""

from PySide6 import QtCore, QtWidgets

class BSBinStatsLabel(QtWidgets.QComboBox):
	"""Display label intended for use in a `QScrollArea` widget"""

	DEFAULT_TEXT = [
		QtCore.QCoreApplication.tr("Showing {filtered_item_count} of {source_item_count} items"),
		QtCore.QCoreApplication.tr("Showing {filtered_column_count} of {source_column_count} columns"),
		QtCore.QCoreApplication.tr("Showing {filtered_item_count} items; {filtered_column_count} columns"),
	]

	def __init__(
		self,
		*args,
		font_scale:float=0.8,
		char_width:int=32,  # len("Showing 999,999 of 999,999 items")
		filter_model:QtCore.QSortFilterProxyModel|None=None,
		source_model:QtCore.QAbstractItemModel|None=None,
		**kwargs
	):

		super().__init__(*args, **kwargs)

		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, self.sizePolicy().verticalPolicy())
#		self.setAlignment (QtCore.Qt.AlignmentFlag.AlignCenter)
#		self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel|QtWidgets.QFrame.Shadow.Sunken)

		f = self.font()
		f.setPointSizeF(f.pointSizeF() * font_scale)
		self.setFont(f)
		
		self.setMinimumWidth(self.fontMetrics().averageCharWidth() * char_width)

		self._filter_model:QtCore.QSortFilterProxyModel = filter_model or QtCore.QSortFilterProxyModel(parent=self)
		self._source_model:QtCore.QAbstractItemModel    = source_model or self._filter_model.sourceModel()
		self._source_model_connections = []

		self._last_index = 0

		self.activated.connect(self.selectedIndexChanged)

		self._setupModel()
		self._setupSourceModel()

	@QtCore.Slot(int)
	def selectedIndexChanged(self, selected_index:int):

		self._last_index = selected_index

	def _setupModel(self):

		self._filter_model.layoutChanged   .connect(self.modelDataChanged)
		self._filter_model.rowsInserted    .connect(self.modelDataChanged),
		self._filter_model.columnsInserted .connect(self.modelDataChanged),
		self._filter_model.rowsRemoved     .connect(self.modelDataChanged),
		self._filter_model.columnsRemoved  .connect(self.modelDataChanged),
		self._filter_model.modelReset      .connect(self.modelDataChanged)

	@QtCore.Slot()
	def _setupSourceModel(self):

		for c in self._source_model_connections:
			self.disconnect(c)

		self._source_model_connections = [
			self._source_model.rowsInserted    .connect(self.modelDataChanged),
			self._source_model.columnsInserted .connect(self.modelDataChanged),
			self._source_model.rowsRemoved     .connect(self.modelDataChanged),
			self._source_model.columnsRemoved  .connect(self.modelDataChanged),
			self._source_model.modelReset      .connect(self.modelDataChanged),
		]

	@QtCore.Slot()
	def modelDataChanged(self):

		self.clear()

		if not self._source_model:
			self.addItem(self.tr("Nothing loaded"))
			return
		
		if self._source_model.rowCount(QtCore.QModelIndex()) == 0:
			self.addItem(self.tr("No items to show"))
			return
		
		filtered_rows    = self._filter_model.rowCount(QtCore.QModelIndex())
		filtered_columns = self._filter_model.columnCount(QtCore.QModelIndex())
		source_rows      = self._source_model.rowCount(QtCore.QModelIndex())
		source_columns   = self._source_model.columnCount(QtCore.QModelIndex())

		for label_text in self.DEFAULT_TEXT:
			self.addItem(label_text.format(
				filtered_item_count   = QtCore.QLocale.system().toString(filtered_rows),
				source_item_count     = QtCore.QLocale.system().toString(source_rows),
				filtered_column_count = QtCore.QLocale.system().toString(filtered_columns),
				source_column_count   = QtCore.QLocale.system().toString(source_columns),
			))

		self.setCurrentIndex(self._last_index)