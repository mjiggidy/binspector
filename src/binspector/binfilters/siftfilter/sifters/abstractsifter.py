from PySide6 import QtCore
import abc

from ..siftmatchtypes import BSSiftMatchTypes

class BSAbstractSifter(abc.ABC):
	"""An abstract sifter"""

	def __init__(self,
		sift_string:str                    = "",
		match_type :BSSiftMatchTypes       = BSSiftMatchTypes.Contains,
		data_role  :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole
	):

		self._sift_string = sift_string
		self._data_role   = data_role
		self._match_type  = match_type

	@abc.abstractmethod
	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:
		"""This sifter accepts the given index"""

	@abc.abstractmethod
	def isValid(self) -> bool:
		"""This filter is complete and should be used"""

	def siftString(self) -> str:
		"""The user string for which to sift"""

		return self._sift_string

	def matchType(self) -> BSSiftMatchTypes:
		"""How to match the string"""

		return self._match_type
	
	def dataRole(self) -> QtCore.Qt.ItemDataRole:
		"""The model's item data role to be considered for the sift"""

		return self._data_role
	
	def __eq__(self, other) -> bool:

		if type(self) is not type(other):
			return NotImplemented
		
		return self.__dict__ == other.__dict__