from PySide6 import QtCore
from . import BSAbstractSifter
from ....binitems import binitemtypes

import timecode

class BSRangeSifter(BSAbstractSifter):
	"""Sift items for which a specified range contains a specified value"""

	def __init__(
		self,
		sift_string:str,
		data_role  :QtCore.Qt.ItemDataRole|None=QtCore.Qt.ItemDataRole.DisplayRole,
	):
	
		super().__init__()

		self._sift_string = sift_string
		self._data_role   = data_role

	def scope_accepts_index(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid():
			return False
		
		item_range = index.data(self._data_role)

		if item_range is None:
			return False
		
		if isinstance(item_range, timecode.TimecodeRange):

			try:
				# NOTE: Not doing this conversion in __init__ because I'm not sure what item values we'll uncover for now...
				sift_value = timecode.Timecode(self._sift_string, rate=item_range.rate, mode=item_range.mode)

			except Exception as e:
				raise
			
			return sift_value in item_range
		
		else:
			raise NotImplementedError(f"** Sift range not yet supported for {repr(item_range)}")