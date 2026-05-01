from PySide6 import QtCore
from .abstractoption import BSBinSiftAbstractOption

class BSSiftNoColumnOption(BSBinSiftAbstractOption):

	def option_accepts_row(self, index:QtCore.QModelIndex):

		# TODO: Verify

		return False