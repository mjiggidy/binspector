from PySide6 import QtCore
import abc

class BSBinSiftAbstractScope(abc.ABC):

	@abc.abstractmethod
	def scope_accepts_index(self, index:QtCore.QModelIndex) -> bool:
		pass