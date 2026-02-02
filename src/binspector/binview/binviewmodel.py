from __future__ import annotations
import typing
from PySide6 import QtCore

from . import binviewitems

class BSBinViewModel(QtCore.QAbstractItemModel):
	"""Main Bin View Model"""

	DEFAULT_BIN_VIEW_NAME = "Untitled"

	sig_bin_view_name_changed = QtCore.Signal(str)

	def __init__(self, /, bin_view:binviewitems.BSBinViewInfo|None=None, parent:QtCore.QObject|None=None):
		
		super().__init__(parent)

		self._bin_view_name:str = self.DEFAULT_BIN_VIEW_NAME
		self._bin_view_columns:list[binviewitems.BSBinViewColumnInfo] = list()
		
		if bin_view:

			self._bin_view_name    = bin_view.name
			self._bin_view_columns = bin_view.columns

	def setBinViewName(self, name:str):

		if self._bin_view_name == name:
			return
		
		self._bin_view_name = name

		self.sig_bin_view_name_changed.emit(name)

	def addBinColumn(self, bin_column:binviewitems.BSBinViewColumnInfo, row:int|None=None):

		if row:
			self.beginInsertRows(QtCore.QModelIndex(), row, row)
			self._bin_view_columns.insert(row, bin_column)
		else:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
			self._bin_view_columns.append(bin_column)
		
		self.endInsertRows()

	def addBinColumns(self, bin_columns:typing.Iterable[binviewitems.BSBinViewColumnInfo], row:int|None=None):

		bin_columns = list(bin_columns)

		if row:
			self.beginInsertRows(QtCore.QModelIndex(), row, row+len(bin_columns)-1)
			self._bin_view_columns[row:row] = bin_columns
		else:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount()+len(bin_columns)-1)
			self._bin_view_columns.extend(bin_columns)
		
		self.endInsertRows()

	def binColumns(self) -> list[binviewitems.BSBinViewColumnInfo]:

		return self._bin_view_columns


	###


	def parent(self, child_index:QtCore.QModelIndex) -> QtCore.QModelIndex:

		return QtCore.QModelIndex()
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return None

		return len(self._bin_view_columns)
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return None
		
		return 1
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if parent.isValid():
			return None

		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		return self._bin_view_columns[index.row()].data(role)
	
	def setData(self, index:QtCore.QModelIndex, value:typing.Any, /, role:binviewitems.BSBinColumnInfoRole):
		print("In the big bin view model setData====")
		print(index.row())
		item = self._bin_view_columns[index.column()]

		print(item)
		
		self.dataChanged.emit(index, index)
		
		return super().setData(index, value, role)