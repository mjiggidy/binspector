from PySide6 import QtCore
from . import BSAbstractSifter

class BSNoColumnSifter(BSAbstractSifter):
	"""Sift no column"""

	def __init__(self,
		sift_string:str,
		data_role  :QtCore.Qt.ItemDataRole|None = QtCore.Qt.ItemDataRole.DisplayRole
	):
		
		super().__init__()

		self._sift_string = sift_string
		self._data_role   = data_role

	def scope_accepts_index(self, index:QtCore.QModelIndex):

		if not index.isValid() or not self._sift_string:
			return True

		return False