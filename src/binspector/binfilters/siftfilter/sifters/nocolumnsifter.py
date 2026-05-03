from PySide6 import QtCore
from . import BSAbstractSifter

class BSNoColumnSifter(BSAbstractSifter):
	"""Sift no column"""

	def scope_accepts_index(self, index:QtCore.QModelIndex):

		# TODO: Verify

		return False