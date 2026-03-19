import typing, dataclasses
from PySide6 import QtCore, QtGui

from . import binviewsources

#DEFAULT_MODIFIED_SYMBOL = "*"
#"""Symbol appended to the name of a bin view"""
	

class BSBinViewProviderModel(QtCore.QAbstractItemModel):

	sig_session_sources_changed = QtCore.Signal()
	sig_stored_sources_changed  = QtCore.Signal()

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._session_view_sources :list[binviewsources.BSAbstractBinViewSource] = []
		self._stored_view_sources  :list[binviewsources.BSAbstractBinViewSource] = []
	
	def addSessionBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to session memory."""

		separator_offset = 0 if self._session_view_sources else 1

		self.beginInsertRows(QtCore.QModelIndex(), 0, 0 + separator_offset)
		self._session_view_sources.insert(0, binview_source)
		self.endInsertRows()

		self.sig_session_sources_changed.emit()

	@QtCore.Slot(object)
	def addStoredBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to stored collection."""
			
		return self.addStoredBinViewSources([binview_source])

	@QtCore.Slot(object)
	def addStoredBinViewSources(self, binview_sources:typing.Iterable[binviewsources.BSAbstractBinViewSource]) -> bool:
		
		new_sources = [binview_source for binview_source in binview_sources if binview_source not in self.binViewSources()]

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


		print(f"{binview_source} in {self._stored_view_sources}?")

		if binview_source in self._session_view_sources:

			idx_viewsource = self._session_view_sources.index(binview_source)

			# If this is the only binview in the sessions list, I'mma take out the separator too
			separator_offset = 1 if len(self._session_view_sources) == 1 else 0

			self.beginRemoveRows(QtCore.QModelIndex(), idx_viewsource, idx_viewsource + separator_offset)
			self._session_view_sources.pop(idx_viewsource)
			self.endRemoveRows()

		elif binview_source in self._stored_view_sources:

			idx_viewsource = self._stored_view_sources.index(binview_source)
			
			# Factor in session views/separators to get the model row
			idx_modelrow   = idx_viewsource + self._stored_views_row_offset()

			self.beginRemoveRows(QtCore.QModelIndex(), idx_modelrow, idx_modelrow)
			self._stored_view_sources.pop(idx_viewsource)
			self.endRemoveRows()
		
		else:
			raise ValueError("Bin view source unknown")

	def clearSessionViewSources(self):
		"""Delete any ephemeral binviews"""

		if not len(self._session_view_sources):
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._session_view_sources)) # NOTE: Not subtracting 1 because also removing separator
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
		
	def binViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:
		"""All binviews in the collection.  Session and stored alike!  Wow!  Haha cool!"""

		return self._session_view_sources + self._stored_view_sources
	
	def binViewNames(self) -> list[str]:
		"""A list of all binview names.  From me, to me.  There ya go me.  Ya weirdo."""

		return [bvs.name() for bvs in self.binViewSources()]
	
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
			
#			elif item.isModified():
#				return item.name() + DEFAULT_MODIFIED_SYMBOL
			
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