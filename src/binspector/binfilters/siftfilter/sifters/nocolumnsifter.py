from PySide6 import QtCore
from . import BSAbstractSifter

from ..siftmatchtypes import BSSiftMatchTypes

class BSNoColumnSifter(BSAbstractSifter):
	"""Sift no column"""

	def __init__(self,
		sift_string:str                    = "",
		match_type :BSSiftMatchTypes       = BSSiftMatchTypes.Contains,
		data_role  :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole
	):
		
		super().__init__(
			sift_string = sift_string,
			match_type  = match_type,
			data_role   = data_role
		)

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex):

		if not index.isValid() or not self._sift_string:
			return True

		return False
	
	def isValid(self):
		return bool(self._sift_string)