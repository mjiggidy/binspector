from PySide6 import QtCore
from . import BSAbstractSifter
from ..siftmatchtypes import BSSiftMatchTypes

import timecode

class BSRangeSifter(BSAbstractSifter):
	"""Sift items for which a specified range contains a specified value"""

	def __init__(
		self,
		sift_string:str                    = "",
		data_role  :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole,
	):
	

		super().__init__(
			sift_string = sift_string,
			match_type  = BSSiftMatchTypes.Contains,
			data_role   = data_role
		)

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid() or not self._sift_string:
			return False
		
		item_range = index.data(self._data_role)

		if item_range is None:
			return False
		
		if isinstance(item_range, timecode.TimecodeRange):

			try:
				# NOTE: Not doing this conversion in __init__ because I'm not sure what item values we'll uncover for now...

				sift_string_santized = self._sift_string.strip(":; ")
				sift_value = timecode.Timecode(sift_string_santized, rate=item_range.rate, mode=item_range.mode)

			except Exception as e:
				
				return False
			
			return sift_value in item_range
		
		else:
			raise NotImplementedError(f"** Sift range not yet supported for {repr(item_range)}")