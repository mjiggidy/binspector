from PySide6 import QtCore, QtGui
import avbutils
from . import treeview
from .delegates import binitems
from ..models import viewmodels
from ..views.delegates import binitems
from ..core import icons




class BSBinTreeView(treeview.LBTreeView):
	"""QTreeView but nicer"""

	sig_default_sort_columns_changed = QtCore.Slot(object)
	"""TODO: HMMMMMM"""

	DEFAULT_ITEM_PADDING:QtCore.QMargins = QtCore.QMargins(2,4,2,4)

	COLUMN_PADDING_RIGHT:int = 24
	"""Additional whitespace per column"""

	ITEM_DELEGATES_PER_FIELD_ID = {
		51: binitems.BSIconLookupItemDelegate(padding=DEFAULT_ITEM_PADDING),

	}
	"""Specialized one-off fields"""

	ITEM_DELEGATES_PER_FORMAT_ID = {
		avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate(padding=DEFAULT_ITEM_PADDING),
	}
	"""Delegate for generic field formats"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)		

		self.setModel((viewmodels.LBSortFilterProxyModel()))

		self.model().columnsInserted.connect(self.setColumnWidthsFromBinView)

		self.model().columnsInserted.connect(
			lambda parent_index, source_start, source_end:
			self.assignItemDelegates(parent_index, source_start)
		)

		self.model().columnsMoved.connect(
			lambda source_parent,
				source_logical_start,
				source_logical_end, 
				destination_parent,
				destination_logical_start:	# NOTE: Won't work for heirarchical models
			self.assignItemDelegates(destination_parent, min(source_logical_start, destination_logical_start))
		)

		# TODO/TEMP: Prep clip color icons
		self._palette_watcher = icons.BSPaletteWatcherForSomeReason()
		clip_color_delegate = self.ITEM_DELEGATES_PER_FIELD_ID[51]
		clip_color_delegate.iconProvider().addIcon(str(QtGui.QColor()), QtGui.QIcon(icons.BSPalettedClipColorIconEngine(clip_color=QtGui.QColor(), palette_watcher=self._palette_watcher)))
		for color in avbutils.get_default_clip_colors():

			icon_color = QtGui.QColor.fromRgba64(*color.as_rgba16())
			icon = QtGui.QIcon(icons.BSPalettedClipColorIconEngine(clip_color=icon_color, palette_watcher=self._palette_watcher))
			clip_color_delegate.iconProvider().addIcon(str(icon_color), icon)



		self.setItemDelegate(binitems.BSGenericItemDelegate(padding=self.DEFAULT_ITEM_PADDING))

	@QtCore.Slot(object, int, int)
	def assignItemDelegates(self, parent_index:QtCore.QModelIndex, logical_start_column:int):
		"""Assign item delegates starting with the first changed logical row, cascaded through to the end"""

		if parent_index.isValid():
			return
		
		for col in range(logical_start_column, self.model().columnCount()):
			
			field_id     = self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+1)
			format_id    = self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+2)

			item_delegate = self.itemDelegate()


			# Look up specialized fields
			if field_id in self.ITEM_DELEGATES_PER_FIELD_ID:
				item_delegate = self.ITEM_DELEGATES_PER_FIELD_ID[field_id]
			# Look up specialized generic formats
			elif format_id in self.ITEM_DELEGATES_PER_FORMAT_ID:
				item_delegate = self.ITEM_DELEGATES_PER_FORMAT_ID[format_id]
			
			self.setItemDelegateForColumn(col, item_delegate)
	
	@QtCore.Slot(object, int)
	@QtCore.Slot(object, int, int)
	@QtCore.Slot(object, int, int, bool)
	def setColumnWidthsFromBinView(self, parent_index:QtCore.QModelIndex, source_start:int, source_end:int|None=None, autosize_if_undefined:bool=True):

		if parent_index.isValid():
			return
		
		if source_end is None:
			source_end = source_start

		for col_index_logical in range(source_start, source_end+1):
			
			self.setColumnWidthFromBinView(
				col_index_logical,
				autosize_if_undefined
			)
	
	@QtCore.Slot(int)
	@QtCore.Slot(int, bool)
	def setColumnWidthFromBinView(self, col_index_logical:int, autosize_if_undefined:bool=True):
		"""Set column width from stored bin view, or resize to contents"""

		column_width = self.model().headerData(
			col_index_logical,
			QtCore.Qt.Orientation.Horizontal,
			QtCore.Qt.ItemDataRole.UserRole+4	# Column width, if specified by bin view
		)
		
		if column_width:
			self.setColumnWidth(col_index_logical, column_width + self.COLUMN_PADDING_RIGHT)
		
		elif autosize_if_undefined:
			self.resizeColumnToContents(col_index_logical)

	def sizeHintForColumn(self, column):
		return super().sizeHintForColumn(column) + self.COLUMN_PADDING_RIGHT
	
	@QtCore.Slot(object)
	def setDefaultSortColumns(self, sort_columns:list[list[int,str]]):

		self._default_sort = sort_columns
		self.sig_default_sort_columns_changed.emit(self._default_sort)