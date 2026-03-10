import abc
from os import PathLike
from PySide6 import QtCore, QtGui, QtWidgets

from . import binviewsources, binviewitemtypes
	

class BSBinViewProviderModel(QtCore.QAbstractItemModel):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._active_views :list[binviewsources.BSAbstractBinViewSource] = []
		self._saved_views  :list[binviewsources.BSAbstractBinViewSource] = []
	
	def addBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource):

		if binview_source.sourceType() == binviewsources.BSBinViewSourceType.Bin:
			
			if binview_source not in self._active_views:

				self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
				self._active_views.insert(0, binview_source)
				self.endInsertRows()

		elif binview_source.sourceType() == binviewsources.BSBinViewSourceType.File:
			
			if binview_source not in self._saved_views:

				self.beginInsertRows(QtCore.QModelIndex(), len(self._saved_views), len(self._saved_views))
				self._saved_views.insert(0, binview_source)
				self.endInsertRows()
		
		else:
			raise ValueError(f"Unknown bin view source type: {repr(binview_source.sourceType())}")
	
	def removeBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource):

		if binview_source.sourceType() == binviewsources.BSBinViewSourceType.Bin:
			
			try:
				idx_view = self._active_views.index(idx_view)

			except ValueError:
				return
			
			else:

				self.beginRemoveRows(QtCore.QModelIndex(), idx_view, idx_view)
				self._active_views.pop(idx_view)
				self.endRemoveRows()

		elif binview_source.sourceType() == binviewsources.BSBinViewSourceType.File:

			try:
				idx_view = self._saved_views.index(binview_source)
			except ValueError:
				return
			
			else:

				start = len(self._active_views) + idx_view
				
				self.beginRemoveRows(QtCore.QModelIndex(), start, start)
				self._saved_views.pop(idx_view)
				self.endRemoveRows()

	def itemForRow(self, row:int) -> binviewsources.BSAbstractBinViewSource:
		"""Get a bin view source given a model row"""

		if row < len(self._active_views):
			return self._active_views[row]

		else:
			return self._saved_views[row - len(self._active_views)]

	###

	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		return False
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 1
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		return len(self._active_views) + len(self._saved_views)
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column, None)
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		if not index.isValid():
			return
		
		item = self.itemForRow(index.row())
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return item.name()
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderVisiting if item.sourceType() == binviewsources.BSBinViewSourceType.File else QtGui.QIcon.ThemeIcon.DriveHarddisk) 
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
			return item.path() if item.sourceType() == binviewsources.BSBinViewSourceType.File else "Loaded From Active Bin"
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return item