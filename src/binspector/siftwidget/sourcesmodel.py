"""
A `QAbstractItemModel` describing bin view columns available for sifting.

The Sift Column chooser shows, in order:

None
---
[All visible columns]
---
[All ranges where beginning of the pair is visible] (Ex: "Start" is visible "Start to End Range")
---
Any

When ranges are selected, only "Contains:" can be selected.  Otherwise defaults to "Any" column

Sorting is not done live!  User needs to click "Apply."  Changing data or bin views has no effect on sift until re-sifted.

When a column or range is selected, but the binview changes so the appropriate column is no longer visibile,
sift goes back to "Any" column.
"""

import enum
from PySide6 import QtCore, QtGui
from ..binview import binviewmodel

from . import rangesmodel

class BSSiftSourceType(enum.Enum):
	"""None? Any? A column? A range? YOU TELL ME, FRIENDOOOOO"""

	NoColumn     = enum.auto()
	SingleColumn = enum.auto()
	Range        = enum.auto()
	AnyColumn    = enum.auto()


class BSSiftSourcesViewModel(QtCore.QAbstractItemModel):
	"""A view model for choosing sifters for sifting"""

	SEPARATOR_ROW_SIZE = 1
	"""How many rows a separator occupies i dunno"""

	sig_bin_view_model_changed = QtCore.Signal(object)

	def __init__(self, *args, bin_view_model:binviewmodel.BSBinViewModel, **kwargs):

		super().__init__(*args, **kwargs)

		self._sift_ranges_model = rangesmodel.BSSiftRangesProxyModel(parent=self)
		self._sift_ranges_model.setSourceModel(bin_view_model)

		self._source_models:dict[BSSiftSourceType, QtCore.QAbstractItemModel] = {
			BSSiftSourceType.NoColumn:  QtGui.QStandardItemModel(parent=self),
			BSSiftSourceType.SingleColumn: bin_view_model,
			BSSiftSourceType.Range: self._sift_ranges_model,
			BSSiftSourceType.AnyColumn: QtGui.QStandardItemModel(parent=self),
		}

		self._source_models[BSSiftSourceType.NoColumn] .appendRow(QtGui.QStandardItem("None"))
		self._source_models[BSSiftSourceType.AnyColumn].appendRow(QtGui.QStandardItem("Any"))
		
		self._reset_count = 0

		# lol three days of troubleshooting and it turns out I didn't call this
		for source_key in self._source_models:
			self._setupSourceModel(source_key)

	
	def _setupSourceModel(self, source_key:BSSiftSourceType):

		model = self._source_models[source_key]

		model.rowsAboutToBeInserted  .connect(self.sourceViewRowsAboutToBeInserted)
		model.rowsAboutToBeMoved     .connect(self.sourceViewRowsAboutToBeMoved)
		model.rowsAboutToBeRemoved   .connect(self.sourceViewRowsAboutToBeRemoved)

		model.rowsInserted           .connect(self.sourceViewRowsInserted)
		model.rowsMoved              .connect(self.sourceViewRowsMoved)
		model.rowsRemoved            .connect(self.sourceViewRowsRemoved)
	
		model.layoutAboutToBeChanged .connect(self.sourceViewLayoutAboutToBeChanged)
		model.layoutChanged          .connect(self.sourceViewLayoutChanged)

		model.modelAboutToBeReset    .connect(self.sourceViewModelAboutToBeReset)
		model.modelReset             .connect(self.sourceViewModelReset)

		model.dataChanged            .connect(self.sourceViewDataChanged)

	###

	def _sourceTypeForModel(self, model:QtCore.QAbstractItemModel) -> BSSiftSourceType:

		return next(k for k,v in self._source_models.items() if v == model)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceViewRowsAboutToBeInserted(self, parent:QtCore.QModelIndex, first:int, last:int) -> None:

		if parent.isValid():
			return
		
		source_type = self._sourceTypeForModel(self.sender())
		offset     = self.rowOffsetToSiftSource(source_type)

		self.beginInsertRows(QtCore.QModelIndex(), first + offset, last + offset)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceViewRowsInserted(self, parent:QtCore.QModelIndex, first:int, last:int) -> None:

		if parent.isValid():
			return

		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceViewRowsAboutToBeMoved(self, sourceParent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destinationParent:QtCore.QModelIndex, destinationRow:int) -> None:

		if sourceParent.isValid() or destinationParent.isValid():

			# NOTE: Assuming we're all flat lists here.
			# Otherwise I guess if either parent index is True, need to translate these into insert/remove rows instead

			return
		
		source_type = self._sourceTypeForModel(self.sender())
		offset      = self.rowOffsetToSiftSource(source_type)

		self.beginMoveRows(QtCore.QModelIndex(), sourceStart + offset, sourceEnd + offset, QtCore.QModelIndex(), destinationRow + offset)

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceViewRowsMoved(self, sourceParent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destinationParent:QtCore.QModelIndex, destinationRow:int) -> None:

		if sourceParent.isValid() or destinationParent.isValid():
			return

		self.endMoveRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceViewRowsAboutToBeRemoved(self, parent:QtCore.QModelIndex, first:int, last:int) -> None:

		if parent.isValid():
			return
		
		source_type = self._sourceTypeForModel(self.sender())
		offset      = self.rowOffsetToSiftSource(source_type)

		self.beginRemoveRows(QtCore.QModelIndex(), first + offset, last + offset)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceViewRowsRemoved(self, parent:QtCore.QModelIndex, first:int, last:int) -> None:

		if parent.isValid():
			return
		
		self.endRemoveRows()

	@QtCore.Slot(list, object)
	def sourceViewLayoutAboutToBeChanged(self, parents:list[QtCore.QPersistentModelIndex]=None, hint:QtCore.QAbstractItemModel.LayoutChangeHint=None) -> None:

		# If parents are defined
		if parents and all(idx.isValid() for idx in parents):
			return
		
		if hint == QtCore.QAbstractItemModel.LayoutChangeHint.HorizontalSortHint:
			return
		
		self.layoutAboutToBeChanged.emit([], hint)

	@QtCore.Slot(list)
	def sourceViewLayoutChanged(self, parents:list[QtCore.QPersistentModelIndex], hint:QtCore.QAbstractItemModel.LayoutChangeHint) -> None:

		if not any(not idx.isValid() for idx in parents):
			return
		
		self.layoutChanged.emit([], hint)

	@QtCore.Slot()
	def sourceViewModelAboutToBeReset(self) -> None:
		
		if self._reset_count == 0:
#			print("**FINNA RESET")
			self.beginResetModel()

#		else:
#			print("** NAH NOT RESET AGAIN")

		self._reset_count += 1
		

	@QtCore.Slot()
	def sourceViewModelReset(self) -> None:

		self._reset_count -= 1
		
		if self._reset_count == 0:
#			print("** DOIN IT")
			self.endResetModel()
		
		elif self._reset_count < 0:
			raise RuntimeError(f"End model reset called {abs(self._reset_count)} extra times...")
		
#		else:
#			print("** NO")

	@QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex, list)
	def sourceViewDataChanged(self, topLeft:QtCore.QModelIndex, bottomRight:QtCore.QModelIndex, roles:list[QtCore.Qt.ItemDataRole]) -> None:
		
		if topLeft.column() != 0:
			return
		
		source_type = self._sourceTypeForModel(self.sender())
		offset      = self.rowOffsetToSiftSource(source_type)
		
		self.dataChanged.emit(
			self.index(topLeft.row()     + offset, 0, QtCore.QModelIndex()),
			self.index(bottomRight.row() + offset, 0, QtCore.QModelIndex()),
			roles
		)

	###
	
	def setBinViewModel(self, model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model"""

		# NOTE: Am I hard-coding this or no?  Need to clean up.

		if BSSiftSourceType.SingleColumn in self._source_models and self._source_models[BSSiftSourceType.SingleColumn] == model:
			return
		
		self.beginResetModel()

		if BSSiftSourceType.SingleColumn in self._source_models:

			self._source_models[BSSiftSourceType.SingleColumn].disconnect(self)

		
		if BSSiftSourceType.Range in self._source_models:

			self._source_models[BSSiftSourceType.Range].setSourceModel(model)
		
		
		self._source_models[BSSiftSourceType.SingleColumn] = model
		self._setupSourceModel(BSSiftSourceType.SingleColumn)

		self.endResetModel()

		self.sig_bin_view_model_changed.emit(model)

	def binViewModel(self) -> binviewmodel.BSBinViewModel:
		"""Get the source bin view model"""

		return self._source_models[BSSiftSourceType.SingleColumn]
	
	###
	
	def _rowCountForSiftSource(self, sift_source_type:BSSiftSourceType, append_separator_if_enabled:bool=True) -> int:
		"""Calculate the number of rows for a given column source section.  Appends a separator assuming it's enabled."""

		row_count = 0

		if sift_source_type not in self._source_models:
			raise ValueError(f"Source type {sift_source_type} is not in this model")
			
		row_count = self._source_models[sift_source_type].rowCount(QtCore.QModelIndex())

		# Add separator to "end" if any rows were present

		if row_count and append_separator_if_enabled:
			return row_count + self.SEPARATOR_ROW_SIZE
		
		else:
			return 0
	
	def rowOffsetToSiftSource(self, to_sift_source:BSSiftSourceType|None=None) -> int:
		"""Calculate the model's row offset to a given sift source section (or 'SSS')"""

		if to_sift_source is not None and to_sift_source not in self._source_models:
			raise ValueError(f"Source type {to_sift_source} is not in this model")
		
		row_offset = 0
		
		for current_sift_source in self._source_models:

			if to_sift_source is not None and to_sift_source == current_sift_source:
				return row_offset
			
			row_offset += self._rowCountForSiftSource(current_sift_source)
		
		return row_offset
	
	def _sourceTypeForIndex(self, index:QtCore.QModelIndex) -> BSSiftSourceType|None:
		"""Map er back"""

		row = index.row()

		accumulated_rows = 0

		for source_type in self._source_models:

			source_row_count = self._rowCountForSiftSource(source_type)
			
			if not source_row_count:
				continue

			accumulated_rows += source_row_count
			
			if row < accumulated_rows - self.SEPARATOR_ROW_SIZE:
				return source_type
			
			if row < accumulated_rows:
				return None
		
		raise IndexError(f"Model does not contain row {repr(index)}")
		
####

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		
		if parent.isValid():
			return 0

		# Remove the final separator (if any rows exist at all) and return row count
		return max(self.rowOffsetToSiftSource() - self.SEPARATOR_ROW_SIZE, 0)

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		
		return 0 if parent.isValid() else 1
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		
		return False
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return self.createIndex(row, column, None)
	
	def flags(self, index:QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
		
		if self._sourceTypeForIndex(index) is None:
			return QtCore.Qt.ItemFlag.NoItemFlags | QtCore.Qt.ItemFlag.ItemNeverHasChildren
		
		return super().flags(index) | QtCore.Qt.ItemFlag.ItemNeverHasChildren

	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		source_type = self._sourceTypeForIndex(index)

		if source_type is None: # Is separator:

			if role == QtCore.Qt.ItemDataRole.AccessibleDescriptionRole:
				return "separator"
			
			return None

		# Map back to bin view model for any single-column data
		row_offset   = self.rowOffsetToSiftSource(source_type)
		source_index = self._source_models[source_type].index(index.row() - row_offset, 0, QtCore.QModelIndex())

		if role == QtCore.Qt.ItemDataRole.UserRole:
			return (source_type, source_index.data(QtCore.Qt.ItemDataRole.UserRole))
		
		return source_index.data(role)