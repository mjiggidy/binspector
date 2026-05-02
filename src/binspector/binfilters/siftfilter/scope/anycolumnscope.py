import typing

import avbutils
from PySide6 import QtCore

from . import BSBinSiftAbstractScope

class BSSiftScopeAnyColumn(BSBinSiftAbstractScope):
	"""Sift option involving a single column"""

	def __init__(
		self,
		sift_rule:avbutils.bins.BinSiftMethod,
		sift_string:str,
		sift_role:QtCore.Qt.ItemDataRole|None=QtCore.Qt.ItemDataRole.DisplayRole
	):

		super().__init__()

		self._sift_rule        = sift_rule
		self._sift_string      = sift_string
		self._sift_role        = sift_role

	def option_accepts_row(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid():
			return False
		
		for col in self.filter_columns(index):

			source_data = str(index.siblingAtColumn(col).data(self._sift_role)) if not None else ""
			sift_string = self._sift_string

			if not self.caseSensitive():
				
				source_data = source_data.casefold()
				sift_string = sift_string.casefold()

			if self._sift_rule == avbutils.bins.BinSiftMethod.BEGINS_WITH:
				return source_data.startswith(sift_string)

			elif self._sift_rule == avbutils.bins.BinSiftMethod.CONTAINS:
				return sift_string in source_data

			elif self._sift_rule == avbutils.bins.BinSiftMethod.MATCHES_EXACTLY:
				return source_data == sift_string

			return ValueError(f"Unsupported sift rule: {self._sift_rule}")
		
	def filter_columns(self, index:QtCore.QModelIndex) -> typing.Generator[QtCore.QModelIndex, None, None]:
		"""Filter columns considered for sift"""

		yield from range(index.model().columnCount(QtCore.QModelIndex()))
	
	def caseSensitive(self) -> bool:
		return False