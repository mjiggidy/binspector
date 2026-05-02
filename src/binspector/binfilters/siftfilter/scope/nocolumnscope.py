from PySide6 import QtCore
from . import BSBinSiftAbstractScope

class BSSiftScopeNoColumn(BSBinSiftAbstractScope):

	def scope_accepts_index(self, index:QtCore.QModelIndex):

		# TODO: Verify

		return False