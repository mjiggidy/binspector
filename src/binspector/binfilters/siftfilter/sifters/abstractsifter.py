from PySide6 import QtCore
import abc

from ..siftmatchtypes import BSSiftMatchTypes

class BSAbstractSifter(abc.ABC):
	"""An abstract sifter"""

	@abc.abstractmethod
	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:
		"""This sifter accepts the given index"""

	@abc.abstractmethod
	def isValid(self) -> bool:
		"""This filter is complete and should be used"""

	@abc.abstractmethod
	def siftString(self) -> str:
		"""The user string for which to sift"""

	@abc.abstractmethod
	def matchType(self) -> BSSiftMatchTypes:
		"""How to match the string"""

