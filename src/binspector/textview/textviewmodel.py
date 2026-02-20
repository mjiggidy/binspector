"""TextViewModel to combine Item Model and View Models"""
import typing
from PySide6 import QtCore

from ..binitems import binitemsmodel, binitemtypes
from ..binview import binviewmodel, binviewitemtypes

import avbutils

class BSTextViewModel(QtCore.QAbstractItemModel):
	"""Combine bin items model with bin view model for a nice table-y text view"""

	def __init__(self, *args, item_model:binitemsmodel.BSBinItemModel|None=None, view_model:binviewmodel.BSBinViewModel|None=None, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._item_model:binitemsmodel.BSBinItemModel = item_model or binitemsmodel.BSBinItemModel()
		self._view_model:binviewmodel.BSBinViewModel  = view_model or binviewmodel.BSBinViewModel()

		self._setupViewModel()
		self._setupItemModel()

	def _setupItemModel(self):

		self._item_model.rowsAboutToBeInserted.connect(self.binItemsAboutToBeInserted)
		self._item_model.rowsInserted.connect(self.binItemsInserted)

		self._item_model.rowsAboutToBeMoved.connect(self.rowsAboutToBeMoved)
		self._item_model.rowsMoved.connect(self.rowsMoved)
		
		self._item_model.rowsAboutToBeRemoved.connect(self.rowsAboutToBeRemoved)
		self._item_model.rowsRemoved.connect(self.rowsRemoved)

		self._item_model.layoutAboutToBeChanged.connect(lambda: self.layoutAboutToBeChanged.emit(hint=QtCore.QAbstractItemModel.LayoutChangeHint.VerticalSortHint))
		self._item_model.layoutChanged.connect(lambda: self.layoutChanged.emit(hint=QtCore.QAbstractItemModel.LayoutChangeHint.VerticalSortHint))

		self._item_model.modelAboutToBeReset.connect(self.modelAboutToBeReset)
		self._item_model.modelReset.connect(self.modelReset)

	def _setupViewModel(self):

		self._view_model.rowsAboutToBeInserted.connect(self.columnsAboutToBeInserted)
		self._view_model.rowsInserted.connect(self.columnsInserted)

		self._view_model.rowsAboutToBeMoved.connect(self.columnsAboutToBeMoved)
		self._view_model.rowsMoved.connect(self.columnsMoved)

		self._view_model.rowsAboutToBeRemoved.connect(self.columnsAboutToBeRemoved)
		self._view_model.rowsRemoved.connect(self.columnsRemoved)

		self._view_model.layoutAboutToBeChanged.connect(lambda: self.layoutAboutToBeChanged.emit(hint=QtCore.QAbstractItemModel.LayoutChangeHint.HorizontalSortHint))
		self._view_model.layoutChanged.connect(lambda: self.layoutChanged.emit(hint=QtCore.QAbstractItemModel.LayoutChangeHint.HorizontalSortHint))

		self._view_model.modelAboutToBeReset.connect(self.modelAboutToBeReset)
		self._view_model.modelReset.connect(self.modelReset)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsAboutToBeInserted(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):
		

		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsInserted(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):
		
		self.endInsertRows()


	def setBinItemModel(self, item_model:binitemsmodel.BSBinItemModel):
		"""Set the bin item model"""

		if self._item_model == item_model:
			return
		
		self._item_model.disconnect(self)

		self.beginResetModel()
		self._item_model = item_model
		self.endResetModel()

	def setBinViewModel(self, view_model:binviewmodel.BSBinViewModel):
		"""Set the bin column view model"""

		if self._view_model == view_model:
			return
		
		self._view_model.disconnect(self)

		self.beginResetModel()
		self._view_model = view_model
		self.endResetModel()


	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Get bin item count"""
		
		if parent.isValid():
			return 0
		
		
		
		return self._item_model.rowCount(QtCore.QModelIndex())
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Get bin view column count"""
		
		if parent.isValid():
			return 0
		
		return self._view_model.rowCount(QtCore.QModelIndex())
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		
		return not parent.isValid()
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		if not row < self._item_model.rowCount(QtCore.QModelIndex()) or not column < self._view_model.rowCount(QtCore.QModelIndex()):
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		#print(f"AKSI INGRG FOR DATAERS {index=} {role=}")
		#return "NO HAHA"

		bin_item = self._item_model.data(self._item_model.index(index.row(), 0, QtCore.QModelIndex()), binitemtypes.BSBinItemDataRoles.ViewItemRole)
		
		# Determine which field we need for this column
		field_id   = self._view_model.data(self._view_model.index(index.column(), 0, QtCore.QModelIndex()), binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		field_name = self._view_model.data(self._view_model.index(index.column(), 0, QtCore.QModelIndex()), binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

		# No info for requested field ID
		if field_id not in bin_item:
			return None
		
		# One of the user fields requested
		elif field_id == avbutils.bins.BinColumnFieldIDs.User:

			# Get column name and look it up in user fields
			user_fields = bin_item[field_id]
			
			if field_name in user_fields:
				return user_fields[field_name].data(role)

		# Return standard field data
		else:
			return bin_item[field_id].data(role)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		
		if not orientation == QtCore.Qt.Orientation.Horizontal:
			return None
		
		return self._view_model.data(self._view_model.index(section, 0, QtCore.QModelIndex()), role)