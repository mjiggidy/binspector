from PySide6 import QtCore

class BSBinItemModel(QtCore.QAbstractItemModel):
	"""Single-column item model for bin items"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._bin_items = []

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Number of bin items"""
		
		return 0 if parent.isValid() else len(self._bin_items)

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Column count for model (returns `1` for flat model)"""

		return 0 if parent.isValid() else 1
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		"""Model is flat and has no children"""
		
		return not parent.isValid()
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Model is flat, children have no parents"""
		
		return QtCore.QModelIndex()