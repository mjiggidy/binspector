from PySide6 import QtCore, QtWidgets

class LBTreeView(QtWidgets.QTreeView):
	"""QTreeView with muh defaults"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setSortingEnabled(True)
		self.setRootIsDecorated(False)
		self.setAlternatingRowColors(True)
		self.setUniformRowHeights(True)

		self.header().setFirstSectionMovable(True)
		self.header().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

	def columnDisplayNames(self) -> list[str]:
		"""Get all column display names, in order"""
		
		return [
			self.model().headerData(idx,
				QtCore.Qt.Orientation.Horizontal,
				QtCore.Qt.ItemDataRole.DisplayRole
			)
			for idx in range(self.header().count())
		]
	
	@QtCore.Slot()
	def resizeAllColumnsToContents(self):
		"""Generic resize-to-fit"""

		for idx in range(self.header().count()):
			self.resizeColumnToContents(idx)
	
	@QtCore.Slot(str, QtCore.Qt.SortOrder)
	def sortByColumnName(self, column_name:str, sort_order:QtCore.Qt.SortOrder) -> bool:
		"""Sort by a column's display name"""

		try:
			header_index = self.columnDisplayNames().index(column_name)
		except ValueError:
			return False

		self.sortByColumn(header_index, sort_order)
		
		return True