from __future__ import annotations
import dataclasses, enum, typing

import avb, avbutils

from PySide6 import QtCore

class BSBinViewColumnInfoRole(enum.IntEnum):
	"""View item data roles available for a given column (extends `QtCore.Qt.ItemDataRole`)"""

	# NOTE: This is good I'mma stick with this.
	# Replaces anything from old view models / binitemtypes whatever

	DisplayNameRole = QtCore.Qt.ItemDataRole.DisplayRole
	"""The name displayed on the bin column header"""

	IconRole        = QtCore.Qt.ItemDataRole.DecorationRole
	"""Data expected by a `BSIconProvider`"""
	
	RawColumnInfo   = QtCore.Qt.ItemDataRole.UserRole
	"""Full `BSBinViewColumnInfo` object"""
	
	FieldIdRole     = QtCore.Qt.ItemDataRole.UserRole + 1
	"""Bin column field identifier"""

	FormatIdRole    = QtCore.Qt.ItemDataRole.UserRole + 2
	"""Bin column data format identifier"""

	IsHiddenRole    = QtCore.Qt.ItemDataRole.UserRole + 3
	"""Bin column visibility"""

	ColumnWidthRole = QtCore.Qt.ItemDataRole.UserRole + 4
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

	_data_roles  :dict[BSBinViewColumnInfoRole, typing.Any] = dataclasses.field(init=False)
	"""View Item Data Roles for `QAbstractItemModel` access via `.data()`"""

	def __post_init__(self):
		self._refresh_data_roles()

	def _refresh_data_roles(self):

		self._data_roles = {
			BSBinViewColumnInfoRole.DisplayNameRole:    self.display_name,
			BSBinViewColumnInfoRole.ColumnWidthRole:    self.column_width,
			BSBinViewColumnInfoRole.FieldIdRole:        self.field_id,
			BSBinViewColumnInfoRole.FormatIdRole:       self.format_id,
			BSBinViewColumnInfoRole.IsHiddenRole:       self.is_hidden,
			BSBinViewColumnInfoRole.RawColumnInfo:      self,
		}


	def data(self, role:BSBinViewColumnInfoRole) -> typing.Any:
		return self._data_roles.get(role, None)
	
	def setData(self, value:typing.Any, role:BSBinViewColumnInfoRole):

		# NOTE: I think `self._data_roles` is updated for free since it's refs?
		# TODO: Verify
		# NOTE: Nope.

		if role == BSBinViewColumnInfoRole.DisplayNameRole:
			self.display_name = value

		elif role == BSBinViewColumnInfoRole.ColumnWidthRole:
			self.column_width = value

		elif role == BSBinViewColumnInfoRole.FieldIdRole:
			self.field_id = value

		elif role == BSBinViewColumnInfoRole.FormatIdRole:
			self.format_id = value
		
		elif role == BSBinViewColumnInfoRole.IsHiddenRole:
			self.is_hidden = value
		
		self._refresh_data_roles()

	@classmethod
	def from_column(cls, bin_column_info:dict, width:int|None=None) -> typing.Self:

		return cls(
			field_id     = avbutils.bins.BinColumnFieldIDs(bin_column_info["type"]),
			format_id    = avbutils.bins.BinColumnFormat(bin_column_info["format"]),
			display_name = str(bin_column_info["title"]),
			column_width = width,
			is_hidden    = bool(bin_column_info["hidden"]),
		)