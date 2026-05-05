import typing

import avbutils
from PySide6 import QtCore

from . import BSAnyColumnSifter
from ..siftmatchtypes import BSSiftMatchTypes
from ....binview import binviewitemtypes

class BSSingleColumnSifter(BSAnyColumnSifter):
	"""Sift items for text in a  single specified column"""

	def __init__(
		self,
		sift_column_info:binviewitemtypes.BSBinViewColumnInfo,
		match_type      :BSSiftMatchTypes,
		sift_string     :str,
		data_role       :QtCore.Qt.ItemDataRole|None=QtCore.Qt.ItemDataRole.DisplayRole
	):
		
		self._sift_column_info = sift_column_info

		super().__init__(
			match_type   = match_type,
			sift_string = sift_string,
			data_role   = data_role
		)

	def filter_columns(self, index:QtCore.QModelIndex) -> typing.Generator[QtCore.QModelIndex, None, None]:
		"""Filter to just the column"""

		# Get sibling index for given header
		source_model  = index.model()

		for col in range(source_model.columnCount(QtCore.QModelIndex())):

			col_field_id = source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
			col_name     = source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

			if col_field_id == self._sift_column_info.field_id:

				# User col: Skip if display name also does not match
				if col_field_id == avbutils.bins.BinColumnFieldIDs.User and col_name != self._sift_column_info.display_name:
					continue

				return col

		raise ValueError(f"Column {self._sift_column_info} not found")

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid() or not self._sift_string:
			return True
		
		col = self.filter_columns(index)
		
		sift_string = self._sift_string
		source_data = str(
			index.siblingAtColumn(col).data(self._data_role)
			if not None else ""
		)
		
		if not self.caseSensitive():

			sift_string = sift_string.casefold()
			source_data = source_data.casefold()
		
		# Match based on match type

		if self._match_type == BSSiftMatchTypes.BeginsWith:

			return source_data.startswith(sift_string)
		
		elif self._match_type == BSSiftMatchTypes.Contains:

			return sift_string in source_data
		
		elif self._match_type == BSSiftMatchTypes.MatchesExactly:

			return sift_string == source_data

		else:
			# SHOULD NEVER HAPPEN
			raise ValueError(f"Unknown match type: {self._match_type}")
		
	def isValid(self):
		return bool(self._sift_string)
	
	def siftColumnInfo(self) -> binviewitemtypes.BSBinViewColumnInfo:

		return self._sift_column_info