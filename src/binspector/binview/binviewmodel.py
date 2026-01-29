from __future__ import annotations
import enum, typing, dataclasses
from PySide6 import QtCore

import avbutils, avb

class BSBinColumnInfoRole(enum.IntEnum):
	"""Bin column info available as a row"""

	DisplayNameRole = QtCore.Qt.ItemDataRole.DisplayRole
	FieldIdRole     = QtCore.Qt.ItemDataRole.UserRole + 1
	FormatIdRole    = FieldIdRole + 1
	IsHiddenRole    = FieldIdRole + 2
	ColumnWidthRole = FieldIdRole + 3

@dataclasses.dataclass
class BSBinViewInfo:

	name:str
	columns:list[BSBinViewColumnInfo]

	@classmethod
	def from_binview(cls, binview:avb.bin.BinViewSetting) -> typing.Self:

		columns = []

		for col in binview.columns:
			try:
				columns.append(BSBinViewColumnInfo.from_column(col))
			except ValueError as e:
				print("Passing value error: ", e)
				continue

		return cls(
			name    = binview.name,
			columns = columns
		)

@dataclasses.dataclass
class BSBinViewColumnInfo:

	field_id     :avbutils.bins.BinColumnFieldIDs
	format_id    :avbutils.bins.BinColumnFormat
	display_name :str
	column_width :int
	is_hidden    :bool

	@classmethod
	def from_column(cls, bin_column_info:dict, width:int|None=None) -> typing.Self:

		return cls(
			field_id     = avbutils.bins.BinColumnFieldIDs(bin_column_info["type"]),
			format_id    = avbutils.bins.BinColumnFormat(bin_column_info["format"]),
			display_name = str(bin_column_info["title"]),
			column_width = width,
			is_hidden    = bool(bin_column_info["hidden"]),
		)

	def data(self, role:BSBinColumnInfoRole):

		if role == BSBinColumnInfoRole.DisplayNameRole:
			return self.display_name
		
		elif role == BSBinColumnInfoRole.FieldIdRole:
			return self.field_id
		
		elif role == BSBinColumnInfoRole.FormatIdRole:
			return self.format_id
		
		elif role == BSBinColumnInfoRole.IsHiddenRole:
			return self.is_hidden
		
		elif role == BSBinColumnInfoRole.ColumnWidthRole:
			return self.column_width
		
		else:
			return None
		

class BSBinViewModel(QtCore.QAbstractItemModel):
	"""Main Bin View Model"""

	sig_bin_view_name_changed = QtCore.Signal(str)

	def __init__(self, /, bin_view:BSBinViewInfo|None=None, parent:QtCore.QObject|None=None):
		
		super().__init__(parent)

		self._bin_view_name:str
		self._bin_view_columns:list[BSBinViewColumnInfo] = list()

		if bin_view:
			self._bin_view_name    = bin_view.name
			self._bin_view_columns = bin_view.columns

	def setBinViewName(self, name:str):

		if self._bin_view_name == name:
			return
		
		self._bin_view_name = name

		self.sig_bin_view_name_changed.emit(name)

	def addBinColumn(self, bin_column:BSBinViewColumnInfo, row:int|None=None):

		if row:
			self.beginInsertRows(QtCore.QModelIndex(), row, row)
			self._bin_view_columns.insert(row, bin_column)
		else:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
			self._bin_view_columns.append(bin_column)
		
		self.endInsertRows()

	def addBinColumns(self, bin_columns:typing.Iterable[BSBinViewColumnInfo], row:int|None=None):

		bin_columns = list(bin_columns)

		if row:
			self.beginInsertRows(QtCore.QModelIndex(), row, row+len(bin_columns)-1)
			self._bin_view_columns[row:row] = bin_columns
		else:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount()+len(bin_columns)-1)
			self._bin_view_columns.extend(bin_columns)
		
		self.endInsertRows()

	def binColumns(self) -> list[BSBinViewColumnInfo]:

		return self._bin_view_columns

	def parent(self, child_index:QtCore.QModelIndex) -> QtCore.QModelIndex:

		return QtCore.QModelIndex()
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return None

		return len(self._bin_view_columns)
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return None
		
		return 1
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if parent.isValid():
			return None

		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole|BSBinColumnInfoRole):

		return self._bin_view_columns[index.row()].data(role)