from PySide6 import QtCore
from . import BSAbstractSifter

from ..siftmatchtypes import BSSiftMatchTypes

class BSNoColumnSifter(BSAbstractSifter):
	"""Sift no column"""

	def __init__(self,
		sift_string:str,
		match_type :BSSiftMatchTypes|None = BSSiftMatchTypes.Contains,
		data_role  :QtCore.Qt.ItemDataRole|None = QtCore.Qt.ItemDataRole.DisplayRole
	):
		
		super().__init__()

		self._sift_string = sift_string
		self._data_role   = data_role
		self._match_type  = match_type

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex):

		if not index.isValid() or not self._sift_string:
			return True

		return False
	
	def isValid(self):
		return bool(self._sift_string)
	
	def matchType(self) -> BSSiftMatchTypes:
		return self._match_type

	def siftString(self) -> str:
		return self._sift_string