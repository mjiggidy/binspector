from __future__ import annotations
import dataclasses, enum, typing

import avb, avbutils

from PySide6 import QtCore

class BSBinColumnInfoRole(enum.IntEnum):
	"""View item data roles available for a given column (extends `QtCore.Qt.ItemDataRole`)"""

	DisplayNameRole = QtCore.Qt.ItemDataRole.DisplayRole
	"""The name displayed on the bin column header"""

	IconRole        = QtCore.Qt.ItemDataRole.DecorationRole
	"""Data expected by a `BSIconProvider`"""
	
	RawColumnInfo   = QtCore.Qt.ItemDataRole.UserRole
	"""Full `BSBinViewColumnInfo` object"""
	
	FieldIdRole     = QtCore.Qt.ItemDataRole.UserRole + 1
	"""Bin column field identifier"""

	FormatIdRole    = FieldIdRole + 1
	"""Bin column data format identifier"""

	IsHiddenRole    = FieldIdRole + 2
	"""Bin column visibility"""

	ColumnWidthRole = FieldIdRole + 3
	"""Saved bin column width"""

@dataclasses.dataclass
class BSBinViewInfo:
	"""BinView View Item Data"""

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

@dataclasses.dataclass()
class BSBinViewColumnInfo:
	"""BinView Column Data"""

	field_id     :avbutils.bins.BinColumnFieldIDs
	"""Column identifier"""

	format_id    :avbutils.bins.BinColumnFormat
	"""Data format represented by this column"""

	display_name :str
	"""Column name for header"""

	column_width :int
	"""Last stored column width"""

	is_hidden    :bool
	"""Column is hidden"""

	_data_roles  :dict[BSBinColumnInfoRole, typing.Any] = dataclasses.field(init=False)
	"""View Item Data Roles for `QAbstractItemModel` access via `.data()`"""

	def __post_init__(self):
		self._refresh_data_roles()

	def _refresh_data_roles(self):

		self._data_roles = {
			BSBinColumnInfoRole.DisplayNameRole:    self.display_name,
			BSBinColumnInfoRole.ColumnWidthRole:    self.column_width,
			BSBinColumnInfoRole.FieldIdRole:        self.field_id,
			BSBinColumnInfoRole.FormatIdRole:       self.format_id,
			BSBinColumnInfoRole.IsHiddenRole:       self.is_hidden,
			BSBinColumnInfoRole.RawColumnInfo:      self,
		}


	def data(self, role:BSBinColumnInfoRole) -> typing.Any:
		return self._data_roles.get(role, None)
	
	def setData(self, value:typing.Any, role:BSBinColumnInfoRole):

		# NOTE: I think `self._data_roles` is updated for free since it's refs?
		# TODO: Verify

		print(f"item bfore: {self.data(role)} but set to {value}")

		if role == BSBinColumnInfoRole.DisplayNameRole:
			self.field_id = value

		elif role == BSBinColumnInfoRole.ColumnWidthRole:
			self.column_width = value

		elif role == BSBinColumnInfoRole.FieldIdRole:
			self.field_id = value

		elif role == BSBinColumnInfoRole.FormatIdRole:
			self.format_id = value
		
		elif role == BSBinColumnInfoRole.IsHiddenRole:
			self.is_hidden = value
		
		self._refresh_data_roles()

		print(f"item after: {self.data(role)}")

		print(self._data_roles)

	@classmethod
	def from_column(cls, bin_column_info:dict, width:int|None=None) -> typing.Self:

		return cls(
			field_id     = avbutils.bins.BinColumnFieldIDs(bin_column_info["type"]),
			format_id    = avbutils.bins.BinColumnFormat(bin_column_info["format"]),
			display_name = str(bin_column_info["title"]),
			column_width = width,
			is_hidden    = bool(bin_column_info["hidden"]),
		)