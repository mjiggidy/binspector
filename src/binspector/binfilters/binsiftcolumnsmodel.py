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

import enum, dataclasses
import avbutils
from PySide6 import QtCore
from ..binview import binviewmodel, binviewitemtypes

class BSBinSiftSourceType(enum.Enum):
	"""None? Any? A column? A range? YOU TELL ME, FRIENDOOOOO"""

	NoColumn         = enum.auto()
	IndividualColumn = enum.auto()
	Range            = enum.auto()
	AnyColumn        = enum.auto()

@dataclasses.dataclass(frozen=True)
class BSBinSiftColumnRowMapper: # wat
	"""Maps rows to their sources ok"""

	local_row:int
	source_type:BSBinSiftSourceType

class BSBinSiftColumnsModel(QtCore.QAbstractItemModel):
	"""A `QAbstractItemModel` describing bin view columns available for sifting"""

	DEFAULT_LIST_ORDER = [
		BSBinSiftSourceType.NoColumn,
		BSBinSiftSourceType.IndividualColumn,
		BSBinSiftSourceType.Range,
		BSBinSiftSourceType.AnyColumn,
	]

	SEPARATOR_ROW_SIZE = 1
	"""How many rows a separator occupies i dunno"""

	sig_bin_view_model_changed = QtCore.Signal(object)

	def __init__(self, *args, bin_view_model:binviewmodel.BSBinViewModel|None=None, list_order:list[BSBinSiftSourceType]|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._list_order         = list_order     or self.DEFAULT_LIST_ORDER
		self._bin_view_model     = bin_view_model or binviewmodel.BSBinViewModel()

		self._dumb_row_map_thing:list[BSBinSiftColumnRowMapper] = []
		
		# lol three days of troubleshooting and it turns out I didn't call this
		self._setupBinViewModel()

	
	def _setupBinViewModel(self):

		self._bin_view_model.rowsAboutToBeInserted  .connect(self.binViewRowsAboutToBeInserted)
		self._bin_view_model.rowsAboutToBeMoved     .connect(self.binViewRowsAboutToBeMoved)
		self._bin_view_model.rowsAboutToBeRemoved   .connect(self.binViewRowsAboutToBeRemoved)

		self._bin_view_model.rowsInserted           .connect(self.binViewRowsInserted)
		self._bin_view_model.rowsMoved              .connect(self.binViewRowsMoved)
		self._bin_view_model.rowsRemoved            .connect(self.binViewRowsRemoved)
		
		self._bin_view_model.layoutAboutToBeChanged .connect(self.binViewLayoutAboutToBeChanged)
		self._bin_view_model.layoutChanged          .connect(self.binViewLayoutChanged)

		self._bin_view_model.modelAboutToBeReset    .connect(self.binViewModelAboutToBeReset)
		self._bin_view_model.modelReset             .connect(self.binViewModelReset)

		self._bin_view_model.dataChanged            .connect(self.binViewDataChanged)

	###
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binViewRowsAboutToBeInserted(self, parent: QtCore.QModelIndex, first: int, last: int) -> None:

		
		mapped_first = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(first, BSBinSiftSourceType.IndividualColumn))
		mapped_last  = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(last,  BSBinSiftSourceType.IndividualColumn))

		self.beginInsertRows(QtCore.QModelIndex(), mapped_first, mapped_last)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binViewRowsInserted(self, parent: QtCore.QModelIndex, first: int, last: int) -> None:

		self._updateRowMap()
		
		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def binViewRowsAboutToBeMoved(self, sourceParent: QtCore.QModelIndex, sourceStart: int, sourceEnd: int, destinationParent: QtCore.QModelIndex, destinationRow: int) -> None:
		
		mapped_first = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(sourceStart,    BSBinSiftSourceType.IndividualColumn))
		mapped_last  = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(sourceEnd,      BSBinSiftSourceType.IndividualColumn))
		mapped_dest  = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(destinationRow, BSBinSiftSourceType.IndividualColumn))

		self.beginMoveRows(QtCore.QModelIndex(), mapped_first, mapped_last, QtCore.QModelIndex(), mapped_dest)

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def binViewRowsMoved(self, sourceParent: QtCore.QModelIndex, sourceStart: int, sourceEnd: int, destinationParent: QtCore.QModelIndex, destinationRow: int) -> None:
		
		self._updateRowMap()

		self.endMoveRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binViewRowsAboutToBeRemoved(self, parent: QtCore.QModelIndex, first: int, last: int) -> None:
		
		mapped_first = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(first, BSBinSiftSourceType.IndividualColumn))
		mapped_last  = self._dumb_row_map_thing.index(BSBinSiftColumnRowMapper(last,  BSBinSiftSourceType.IndividualColumn))

		self.beginRemoveRows(QtCore.QModelIndex(), mapped_first, mapped_last)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binViewRowsRemoved(self, parent: QtCore.QModelIndex, first: int, last: int) -> None:

		self._updateRowMap()

		self.endRemoveRows()

	@QtCore.Slot(list)
	def binViewLayoutAboutToBeChanged(self, parents: list[QtCore.QPersistentModelIndex], hint: QtCore.QAbstractItemModel.LayoutChangeHint) -> None:
		
		self.layoutAboutToBeChanged.emit()

	@QtCore.Slot(list)
	def binViewLayoutChanged(self, parents: list[QtCore.QPersistentModelIndex], hint: QtCore.QAbstractItemModel.LayoutChangeHint) -> None:
		
		self._updateRowMap()
		
		self.layoutChanged.emit()

	@QtCore.Slot()
	def binViewModelAboutToBeReset(self) -> None:
		
		self.beginResetModel()

	@QtCore.Slot()
	def binViewModelReset(self) -> None:
		
		self._updateRowMap()
		
		self.endResetModel()

	@QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex, list)
	def binViewDataChanged(self, topLeft: QtCore.QModelIndex, bottomRight: QtCore.QModelIndex, roles: list[int]) -> None:

		self.beginResetModel()
		self._updateRowMap()
		self.endResetModel()
		
#		offset = self._calculateRowOffsetToSourceSection(BSBinSiftSourceType.IndividualColumn)
#		
#		self.dataChanged.emit(
#			self.index(topLeft.row() + offset, topLeft.column(),QtCore.QModelIndex()),
#			self.index(bottomRight.row() + offset, bottomRight.column(), QtCore.QModelIndex()),
#			roles
#		)

	###
	
	def setBinViewModel(self, model:binviewmodel.BSBinViewModel):
		"""Set the source bin view model"""

		if self._bin_view_model == model:
			return
		
		self.beginResetModel()
		
		self._bin_view_model.disconnect(self)
		self._bin_view_model = model
		self._setupBinViewModel()

		self.endResetModel()

		self.sig_bin_view_model_changed.emit(model)

	def binViewModel(self) -> binviewmodel.BSBinViewModel:
		"""Get the source bin view model"""

		return self._bin_view_model
	
	###

	def _updateRowMap(self):

		self._dumb_row_map_thing = []

		for source_type in self._list_order:

			self._dumb_row_map_thing.extend([
				BSBinSiftColumnRowMapper(local_row, source_type) for local_row in range(self._rowCountForSiftSource(source_type))
			])
	
	def _rowCountForSiftSource(self, sift_source_type:BSBinSiftSourceType) -> int:
		"""Calculate the number of rows for a given column source section"""

		if sift_source_type not in self._list_order:
			raise ValueError(f"Source type {sift_source_type} is not in this model")

		elif sift_source_type == BSBinSiftSourceType.IndividualColumn:

			# Bin View row count

			return self._bin_view_model.rowCount(QtCore.QModelIndex())
		
		else:

			# One-off rows such as "Any" or "None"
			return 1
	
####

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		
		if parent.isValid():
			return 0
		
		return len(self._dumb_row_map_thing)

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		
		return 0 if parent.isValid() else 1
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		
		return False
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return self.createIndex(row, column, None)

	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		
		if not index.isValid():
			return None

		row_mapper = self._dumb_row_map_thing[index.row()]

		if row_mapper.source_type == BSBinSiftSourceType.AnyColumn:

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return self.tr("Any")
			
		elif row_mapper.source_type == BSBinSiftSourceType.NoColumn:

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return self.tr("None")
			
		elif row_mapper.source_type == BSBinSiftSourceType.IndividualColumn:

			# Map back to bin view model for any single-column data
			return self._bin_view_model.index(row_mapper.local_row, 0, QtCore.QModelIndex()).data(role)
			
		elif row_mapper.source_type == BSBinSiftSourceType.Range:

			# TODO: Group

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return self.tr("Value Range")
			
		else:

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return "lolwat" + str(row_mapper.source_type)

		return None
	

"""

Can:
Calculate total rows

Need:
Given an index, wat do
	- Figure out which source type it is
		- Keep adding section lengths until greater than index row
			- 
	- Either show the bin column, or the special lil data



"""