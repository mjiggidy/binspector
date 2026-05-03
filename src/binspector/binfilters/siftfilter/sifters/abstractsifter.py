from PySide6 import QtCore
import abc

class BSAbstractSifter(abc.ABC):
	"""An abstract sifter"""

	@abc.abstractmethod
	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:
		"""This sifter accepts the given index"""

	@abc.abstractmethod
	def isValid(self) -> bool:
		"""This filter is complete and should be used"""