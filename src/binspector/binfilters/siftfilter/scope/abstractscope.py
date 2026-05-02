from PySide6 import QtCore
import abc

class BSBinSiftAbstractScope(abc.ABC):

	@abc.abstractmethod
	def option_accepts_row(self, index:QtCore.QModelIndex) -> bool:
		pass