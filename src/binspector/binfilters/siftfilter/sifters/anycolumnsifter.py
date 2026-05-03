import typing

import avbutils
from PySide6 import QtCore

from ..siftmatchtypes import BSSiftMatchTypes
from . import BSAbstractSifter

class BSAnyColumnSifter(BSAbstractSifter):
	"""Sift items for specified text in any column"""

	def __init__(
		self,
		match_type :BSSiftMatchTypes,
		sift_string:str,
		data_role  :QtCore.Qt.ItemDataRole|None=QtCore.Qt.ItemDataRole.DisplayRole
	):

		super().__init__()

		self._match_type  = match_type
		self._sift_string = sift_string
		self._data_role   = data_role

	def scope_accepts_index(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid() or not self._sift_string:
			return True
		
		for col in self.filter_columns(index):

			source_data = str(
				index.siblingAtColumn(col).data(self._data_role) if not None else "")
			sift_string = self._sift_string

			if not self.caseSensitive():
				
				source_data = source_data.casefold()
				sift_string = sift_string.casefold()

			print(f"** {source_data=} {sift_string=} {self._data_role=} {index=}")

			if self._match_type == avbutils.bins.BinSiftMethod.BEGINS_WITH:
				return source_data.startswith(sift_string)

			elif self._match_type == avbutils.bins.BinSiftMethod.CONTAINS:
				return sift_string in source_data

			elif self._match_type == avbutils.bins.BinSiftMethod.MATCHES_EXACTLY:
				return source_data == sift_string

			return ValueError(f"Unsupported sift rule: {self._match_type}")
		
	def filter_columns(self, index:QtCore.QModelIndex) -> typing.Generator[QtCore.QModelIndex, None, None]:
		"""Filter columns considered for sift"""

		yield from range(index.model().columnCount(QtCore.QModelIndex()))
	
	def caseSensitive(self) -> bool:
		return False