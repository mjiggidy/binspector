import avbutils
from PySide6 import QtCore
from .delegates import binitems
from ..models import viewmodels
from . import treeview

class BSBinTreeView(treeview.LBTreeView):
	"""QTreeView but nicer"""

	ITEM_DELEGATES_PER_FIELD_ID = {
		51: binitems.LBClipColorItemDelegate(),

	}
	"""Specialized one-off fields"""

	ITEM_DELEGATES_PER_FORMAT_ID = {
		avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate(),
	}
	"""Delegate for generic field formats"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)		

		self.setModel((viewmodels.LBSortFilterProxyModel()))

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

	def sizeHintForColumn(self, column):
		return super().sizeHintForColumn(column) + 24