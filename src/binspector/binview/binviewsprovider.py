import abc
from os import PathLike
from PySide6 import QtCore, QtGui, QtWidgets

from . import binviewsources, binviewitemtypes
	

class BSBinViewProviderModel(QtCore.QAbstractItemModel):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._session_views :list[binviewsources.BSAbstractBinViewSource] = []
		self._stored_views  :list[binviewsources.BSAbstractBinViewSource] = []
	
	def addSessionBinView(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to session memory."""
			
		if binview_source in self._session_views:
			return False

		self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
		self._session_views.insert(0, binview_source)
		self.endInsertRows()

	def addStoredBinView(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to stored collection."""
			
		if binview_source in self.allBinViews():
			return False
		
		view_row_offset = self._stored_views_row_offset()

		self.beginInsertRows(QtCore.QModelIndex(), view_row_offset, view_row_offset)
		self._stored_views.insert(0, binview_source)
		self.endInsertRows()
	
	def removeBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource):

		if binview_source.sourceType() == binviewsources.BSBinViewSourceType.Bin:
			
			try:
				idx_view = self._session_views.index(idx_view)

			except ValueError:
				return
			
			else:

				self.beginRemoveRows(QtCore.QModelIndex(), idx_view, idx_view)
				self._session_views.pop(idx_view)
				self.endRemoveRows()

		elif binview_source.sourceType() == binviewsources.BSBinViewSourceType.File:

			try:
				idx_view = self._stored_views.index(binview_source)
			except ValueError:
				return
			
			else:

				start = len(self._session_views) + idx_view
				
				self.beginRemoveRows(QtCore.QModelIndex(), start, start)
				self._stored_views.pop(idx_view)
				self.endRemoveRows()

	def clearSessionViews(self):
		"""Delete any ephemeral binviews"""

		if not len(self._session_views):
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._session_views) -1)
		self._session_views = []
		self.endRemoveRows()

	def clearStoredViews(self):
		"""Delete any permanent binviews"""

		if not len(self._stored_views):
			return
		
		view_row_start = self._stored_views_row_offset()
		view_row_end   = self._stored_views_row_offset() + len(self._stored_views) - 1
		
		self.beginRemoveRows(QtCore.QModelIndex(), view_row_start, view_row_end)
		self._stored_views = []
		self.endRemoveRows()

	def itemForRow(self, row:int) -> binviewsources.BSAbstractBinViewSource:
		"""Get a bin view source given a model row"""

		if row < len(self._session_views):
			return self._session_views[row]

		else:
			return self._stored_views[row - self._stored_views_row_offset()]
		
	def allBinViews(self) -> list[binviewsources.BSAbstractBinViewSource]:
		"""All binviews in the collection"""

		return [self._session_views] + [self._stored_views]
		
	def _stored_views_row_offset(self) -> int:
		"""Return the row offset between stored views indexes and view row indexes"""

		session_count = len(self._session_views)

		return len(self._session_views) + (1 if session_count > 0 else 0)
	
	def _index_is_separator(self, index:QtCore.QModelIndex) -> bool:

		return self._session_views and index.row() == self._stored_views_row_offset()-1

	###

	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		return False
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 1
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		return len(self._session_views) + len(self._stored_views) + (1 if self._session_views else 0)
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column, None)
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		if not index.isValid():
			return
		
		if self._index_is_separator(index):

	#		if role == QtCore.Qt.ItemDataRole.DisplayRole:
	#			return "Saved Bin Views ---"
			if role == QtCore.Qt.ItemDataRole.AccessibleDescriptionRole:
				return "separator"


			else:
				return None
		
		item = self.itemForRow(index.row())
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return item.name()
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderVisiting if item.sourceType() == binviewsources.BSBinViewSourceType.File else QtGui.QIcon.ThemeIcon.DriveHarddisk) 
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
			return item.path() if item.sourceType() == binviewsources.BSBinViewSourceType.File else "Loaded From Active Bin"
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return item
		
	def flags(self, index:QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:

		if self._index_is_separator(index):
			return QtCore.Qt.ItemFlag.NoItemFlags
		
		return super().flags(index)
	
	def clear(self):
		"""Clear and reset the entire model"""

		self.beginResetModel()

		self._session_views = []
		self._stored_views  = []

		self.endResetModel()