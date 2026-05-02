from PySide6 import QtCore
from . import BSBinSiftAbstractScope

class BSSiftScopeNoColumn(BSBinSiftAbstractScope):

	def option_accepts_row(self, index:QtCore.QModelIndex):

		# TODO: Verify

		return False