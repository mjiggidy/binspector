import typing, dataclasses
from PySide6 import QtCore, QtGui

from . import binviewsources
	

class BSBinViewProviderModel(QtCore.QAbstractItemModel):

	sig_session_sources_changed = QtCore.Signal()
	sig_stored_sources_changed  = QtCore.Signal()

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._session_view_sources :list[binviewsources.BSAbstractBinViewSource] = []
		self._stored_view_sources  :list[binviewsources.BSAbstractBinViewSource] = []
	
	def addSessionBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to session memory."""

		self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
		self._session_view_sources.insert(0, binview_source)
		self.endInsertRows()

		self.sig_session_sources_changed.emit()

	@QtCore.Slot(object)
	def addStoredBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to stored collection."""
			
		return self.addStoredBinViewSources([binview_source])

	@QtCore.Slot(object)
	def addStoredBinViewSources(self, binview_sources:typing.Iterable[binviewsources.BSAbstractBinViewSource]) -> bool:
		
		new_sources = [binview_source for binview_source in binview_sources if binview_source not in self.allBinViewSources()]

		if not new_sources:
			return False
		
		view_row_offset = self._stored_views_row_offset()

		self.beginInsertRows(QtCore.QModelIndex(), view_row_offset, view_row_offset + len(new_sources) - 1)
		self._stored_view_sources = new_sources + self._stored_view_sources
		self.endInsertRows()

		self.sig_stored_sources_changed.emit()

		return True
	
	@QtCore.Slot(object)
	def removeBinViewSources(self, binview_sources:typing.Iterable[binviewsources.BSAbstractBinViewSource]) -> bool:

		# NOTE: This is backwards, should be "remove one calls removeMany" but I'm movin' quick right nah

		for binview_source in binview_sources:
			self.removeBinViewSource(binview_source)
	
	def removeBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource):

#		print("REMOVAN ", binview_source.path())

		if binview_source.sourceType() == binviewsources.BSBinViewSourceType.Bin:
			
			try:
				idx_view = self._session_view_sources.index(idx_view)

			except ValueError:
				return
			
			else:

				self.beginRemoveRows(QtCore.QModelIndex(), idx_view, idx_view)
				self._session_view_sources.pop(idx_view)
				self.endRemoveRows()

		elif binview_source.sourceType() == binviewsources.BSBinViewSourceType.File:

			try:
				idx_view = self._stored_view_sources.index(binview_source)
			except ValueError:
				return
			
			else:

				start = len(self._session_view_sources) + idx_view
				
				self.beginRemoveRows(QtCore.QModelIndex(), start, start)
				self._stored_view_sources.pop(idx_view)
				self.endRemoveRows()

	def clearSessionViewSources(self):
		"""Delete any ephemeral binviews"""

		if not len(self._session_view_sources):
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._session_view_sources) -1)
		self._session_view_sources = []
		self.endRemoveRows()

		self.sig_session_sources_changed.emit()

	def clearStoredViewSources(self):
		"""Delete any permanent binviews"""

		if not len(self._stored_view_sources):
			return
		
		view_row_start = self._stored_views_row_offset()
		view_row_end   = self._stored_views_row_offset() + len(self._stored_view_sources) - 1
		
		self.beginRemoveRows(QtCore.QModelIndex(), view_row_start, view_row_end)
		self._stored_view_sources = []
		self.endRemoveRows()

		self.sig_stored_sources_changed.emit()

	def binViewSourceForRow(self, row:int) -> binviewsources.BSAbstractBinViewSource:
		"""Get a bin view source given a model row"""

		if row < len(self._session_view_sources):
			return self._session_view_sources[row]

		else:
			return self._stored_view_sources[row - self._stored_views_row_offset()]
		
	def allBinViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:
		"""All binviews in the collection"""

		return [self._session_view_sources] + [self._stored_view_sources]
	
	def sessionBinViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:
		
		return self._session_view_sources
	
	def storedBinViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:

		return self._stored_view_sources
		
	def _stored_views_row_offset(self) -> int:
		"""Return the row offset between stored views indexes and view row indexes"""

		session_count = len(self._session_view_sources)

		return len(self._session_view_sources) + (1 if session_count > 0 else 0)
	
	def _index_is_separator(self, index:QtCore.QModelIndex) -> bool:

		return self._session_view_sources and index.row() == self._stored_views_row_offset()-1

	###

	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		return False
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 1
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		return len(self._session_view_sources) + len(self._stored_view_sources) + (1 if self._session_view_sources else 0)
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column, None)
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		if not index.isValid():
			return
		
		item = self.binViewSourceForRow(index.row())
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:

			if self._index_is_separator(index):
				return None
			
			else:
				return item.name()

		elif role == QtCore.Qt.ItemDataRole.AccessibleDescriptionRole:
		
			if self._index_is_separator(index):
				return "separator"
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:

			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderVisiting if item.sourceType() == binviewsources.BSBinViewSourceType.File else QtGui.QIcon.ThemeIcon.DriveHarddisk) 
		
		elif role == QtCore.Qt.ItemDataRole.FontRole:

			if item.isModified():
#				print("*******MODIFIED")
				font = QtGui.QFont()
				font.setItalic(True)
				return font
		
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

		self._session_view_sources = []
		self._stored_view_sources  = []

		self.endResetModel()