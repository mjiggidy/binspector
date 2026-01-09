import logging
from PySide6 import QtCore, QtWidgets

from ..models import viewmodels
from ..core import config
from . import sceneitems, painters

class BSBinFrameScene(QtWidgets.QGraphicsScene):
	"""Graphics scene based on a bin model"""

	sig_bin_filter_model_changed   = QtCore.Signal(object)
	sig_selection_model_changed    = QtCore.Signal(object)
	sig_bin_item_added             = QtCore.Signal(object)

	def __init__(self, *args, bin_filter_model:viewmodels.BSBinItemViewModel|None=None, brushes_manager:painters.BSFrameItemBrushManager, **kwargs):

		super().__init__(*args, **kwargs)

		self._bin_filter_model = bin_filter_model or viewmodels.BSBinViewProxyModel()
		self._selection_model  = QtCore.QItemSelectionModel()
		self._brushes_manager  = brushes_manager

		self._bin_items:list[sceneitems.BSFrameModeItem] = list()

		self._z_top = 0

		self._setupModel()
		self._setupSelectionModel()

	def _setupModel(self):

		self._bin_filter_model.rowsInserted  .connect(self.addBinItems)
		self._bin_filter_model.rowsAboutToBeRemoved .connect(self.removeBinItems)
		self._bin_filter_model.modelReset    .connect(self.clear)

		self._bin_filter_model.rowsMoved     .connect(self.reloadBinFilterModel)
		self._bin_filter_model.layoutChanged .connect(self.reloadBinFilterModel)

		self.selectionChanged.connect(self.updateSelectionModel)

	def _setupSelectionModel(self):
		self._selection_model.selectionChanged.connect(self.setSelectedItemsFromSelectionModel)

	def selectionModel(self) -> QtCore.QItemSelectionModel:
		return self._selection_model

	@QtCore.Slot(object)
	def setSelectionModel(self, selection_model:QtCore.QItemSelectionModel):

		if self._selection_model != selection_model:

			self._selection_model.disconnect(self)

			self._selection_model = selection_model
			self._setupSelectionModel()
			self.sig_selection_model_changed.emit(selection_model)

	@QtCore.Slot(object)
	def setSelectedItems(self, item_indexes:list[int]):
		"""Set selected items"""

		for idx, item in enumerate(self._bin_items):
			item.setSelected(idx in item_indexes)

	@QtCore.Slot(object,object)
	def setSelectedItemsFromSelectionModel(self, selected:QtCore.QItemSelection, deselected:QtCore.QItemSelection):
		"""Update selected bin items according to the selection model"""

		#self._selection_model.blockSignals(True)

		for row in set(i.row() for i in selected.indexes()):
			item = self._bin_items[row]
			if not item.isSelected():
				self._bin_items[row].setSelected(True)

		for row in set(i.row() for i in deselected.indexes()):
			item = self._bin_items[row]
			if item.isSelected():
				self._bin_items[row].setSelected(False)

		#self._selection_model.blockSignals(False)

	@QtCore.Slot()
	def updateSelectionModel(self):
		"""Update selection model to mirror the scene's selected items"""

#		print(self.selectedItems())

#		current_rows = set(self._bin_items.index(i) for i in self.selectedItems())
#		stale_rows   = set(i.row() for i in self._selection_model.selection().indexes()) - current_rows


	#	self.blockSignals(True)
#
	#	self._selection_model.clear()
#
	#	for row in current_rows:
#
	#		self._selection_model.select(
	#			self._bin_filter_model.index(row, 0, QtCore.QModelIndex()),
	#			QtCore.QItemSelectionModel.SelectionFlag.Select|
	#			QtCore.QItemSelectionModel.SelectionFlag.Rows
	#		)
#
	#	self.blockSignals(False)

	def binFilterModel(self) -> viewmodels.BSBinViewProxyModel:
		return self._bin_filter_model

	@QtCore.Slot(object)
	def setBinFilterModel(self, bin_model:viewmodels.BSBinViewProxyModel):

		if not self._bin_filter_model == bin_model:

			self._bin_filter_model.disconnect(self)

			self._bin_filter_model = bin_model
			self._setupModel()

			logging.getLogger(__name__).debug("Set bin filter model=%s (source model=%s)", self._bin_filter_model, self._bin_filter_model.sourceModel())
			self.sig_bin_filter_model_changed.emit(bin_model)

	@QtCore.Slot()
	def reloadBinFilterModel(self):
		"""Reset and reload items from bin filter model to stay in sync with order changes"""

		logging.getLogger(__name__).debug("About to clear bin frame view for layout change")
		self.clear()

		self.addBinItems(QtCore.QModelIndex(), 0, self._bin_filter_model.rowCount()-1)
		#self.setSelectedItemsFromSelectionModel(self._selection_model.selection(), QtCore.QItemSelection())

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def addBinItems(self, parent_row_index:QtCore.QModelIndex, row_start:int, row_end:int):

		for row in range(row_start, row_end+1):

			# Resolve source model to ensure we always have relevent columns available
			proxy_row_index  = self._bin_filter_model.index(row, 0, parent_row_index)

			bin_item_name   = proxy_row_index.data(viewmodels.viewmodelitems.BSBinItemDataRoles.BSItemName)
			bin_item_coords = proxy_row_index.data(viewmodels.viewmodelitems.BSBinItemDataRoles.BSFrameCoordinates)
			bin_item_color  = proxy_row_index.data(viewmodels.viewmodelitems.BSBinItemDataRoles.BSClipColor)
			bin_item_type   = proxy_row_index.data(viewmodels.viewmodelitems.BSBinItemDataRoles.BSItemType)

			#print(bin_item_color)

			bin_item = sceneitems.BSFrameModeItem(brush_manager=self._brushes_manager)
			bin_item.setName(str(bin_item_name))
			bin_item.setClipColor(bin_item_color)
			bin_item.setClipType(bin_item_type)
			bin_item.setFlags(config.BSFrameViewConfig.DEFAULT_ITEM_FLAGS)
			
			

			x, y, z = *bin_item_coords, self._z_top
			self._z_top += 1

			bin_item.setPos(QtCore.QPoint(x, y))
			bin_item.setZValue(z)

			self._bin_items.insert(row, bin_item)

			self.addItem(bin_item)

			self.sig_bin_item_added.emit(bin_item)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def removeBinItems(self, parent_row_index:QtCore.QModelIndex, row_start:int, row_end:int):

		for row in range(row_end, row_start-1, -1):

			bin_item = self._bin_items.pop(row)
			self.removeItem(bin_item)

	@QtCore.Slot(object)
	def raiseItemToTop(self, item:QtWidgets.QGraphicsItem):

		self._z_top += 1
		item.setZValue(self._z_top)

	@QtCore.Slot(object)
	def raiseItemsToTop(self, items:list[QtWidgets.QGraphicsItem]):

		for item in sorted(items, key=lambda i: i.zValue()):
			self.raiseItemToTop(item)

	@QtCore.Slot()
	def clear(self):

		self._bin_items.clear()
		logging.getLogger(__name__).debug("Bin frame view cleared")
		return super().clear()