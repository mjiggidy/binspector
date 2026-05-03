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
		source_column = None

		for col in range(source_model.columnCount(QtCore.QModelIndex())):

			col_field_id = source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
			col_name     = source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

			if col_field_id == self._sift_column_info.field_id:

				# User col: Skip if display name also does not match
				if col_field_id == avbutils.bins.BinColumnFieldIDs.User and col_name != self._sift_column_info.display_name:
					continue

				source_column = col
				break

			# Column not present in bin view
			if source_column is None:
				yield False
		
			yield True

	def scope_accepts_index(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid():
			return False
		
		# TODO
		print("TODO: Filter single column")
		return True