import avbutils
from PySide6 import QtCore, QtWidgets
from .delegates import binitems
from ..models import viewmodels

class LBTreeView(QtWidgets.QTreeView):
	"""QTreeView but nicer"""


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
		for idx in range(self.header().count()):
			self.resizeColumnToContents(idx)

	@QtCore.Slot(object)
	def setColumnWidths(self, column_widths:dict[str,int]):

		raise DeprecationWarning("Nah, use bintreeview")

		if not column_widths:

			self.resizeAllColumnsToContents()
			return
		
		column_names = self.columnDisplayNames()

		for col, width in column_widths.items():
		
			try:
				col_idx = column_names.index(col)
			except ValueError:
				continue
		
			self.setColumnWidth(col_idx, width)
	
	@QtCore.Slot(str, QtCore.Qt.SortOrder)
	def sortByColumnName(self, column_name:str, sort_order:QtCore.Qt.SortOrder) -> bool:
		"""Sort by a column's display name"""

		column_names = self.columnDisplayNames()

		try:
			header_index = column_names.index(column_name)
		except ValueError:
			return False

		self.sortByColumn(header_index, sort_order)
		return True