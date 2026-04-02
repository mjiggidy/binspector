"""
Widgets for adding as scrollBarWidgets to `QScrollArea`

Mostly standard widgets sublcassed for style
"""

from PySide6 import QtCore, QtWidgets

class BSBinStatsLabel(QtWidgets.QLabel):
	"""Display label intended for use in a `QScrollArea` widget"""

	DEFAULT_TEXT = "Showing {filtered_item_count} of {source_item_count} items"

	def __init__(
		self,
		*args,
		font_scale:float=0.8,
		char_width:int=32,  # len("Showing 999,999 of 999,999 items")
		filter_model:QtCore.QSortFilterProxyModel|None=None,
		**kwargs
	):

		super().__init__(*args, **kwargs)

		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, self.sizePolicy().verticalPolicy())
		self.setAlignment (QtCore.Qt.AlignmentFlag.AlignCenter)
		self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel|QtWidgets.QFrame.Shadow.Sunken)

		f = self.font()
		f.setPointSizeF(f.pointSizeF() * font_scale)
		self.setFont(f)
		
		self.setMinimumWidth(self.fontMetrics().averageCharWidth() * char_width)

		self._model:QtCore.QSortFilterProxyModel = filter_model or QtCore.QSortFilterProxyModel(parent=self)
		self._source_model_connections = []

		self._setupModel()

	def _setupModel(self):
		
		self._model.sourceModelChanged.connect(self._setupSourceModel)

		self._model.layoutChanged.connect(self.modelDataChanged)
		self._model.rowsInserted    .connect(self.modelDataChanged),
		self._model.columnsInserted .connect(self.modelDataChanged),
		self._model.rowsRemoved     .connect(self.modelDataChanged),
		self._model.columnsRemoved  .connect(self.modelDataChanged),
		self._model.modelReset.connect(self.modelDataChanged)

		if self._model.sourceModel() is not None:
			self._setupSourceModel()

	@QtCore.Slot()
	def _setupSourceModel(self):

		for c in self._source_model_connections:
			self.disconnect(c)

		self._source_model_connections = [
			self._model.sourceModel().rowsInserted    .connect(self.modelDataChanged),
			self._model.sourceModel().columnsInserted .connect(self.modelDataChanged),
			self._model.sourceModel().rowsRemoved     .connect(self.modelDataChanged),
			self._model.sourceModel().columnsRemoved  .connect(self.modelDataChanged),
			self._model.sourceModel().modelReset      .connect(self.modelDataChanged),
		]

	@QtCore.Slot()
	def modelDataChanged(self):

		if not self._model.sourceModel():
			self.setText(self.tr("Nothing loaded"))
			return
		
		if self._model.sourceModel().rowCount(QtCore.QModelIndex()) == 0:
			self.setText(self.tr("No items to show"))
			return
		
		filtered_rows = self._model.rowCount(QtCore.QModelIndex())
		source_rows   = self._model.sourceModel().rowCount(QtCore.QModelIndex())

		self.setText(self.tr(self.DEFAULT_TEXT).format(
			filtered_item_count = QtCore.QLocale.system().toString(filtered_rows),
			source_item_count   = QtCore.QLocale.system().toString(source_rows),
		))