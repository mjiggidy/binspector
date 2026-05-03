from PySide6 import QtCore
import abc

class BSAbstractSifter(abc.ABC):
	"""An abstract sifter"""

	@abc.abstractmethod
	def scope_accepts_index(self, index:QtCore.QModelIndex) -> bool:
		pass