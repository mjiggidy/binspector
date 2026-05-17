from PySide6 import QtWidgets, QtCore

from . import editordelegates, editorproxymodel
from ..binview import binviewitemtypes

class BSBinViewColumnListView(QtWidgets.QTableView):
	"""A QTableView for bin view column data"""

	def __init__(self):

		super().__init__()

		self.setItemDelegate(editordelegates.BSBinViewColumnDelegate())
		
		# Background 'n' grid
		self.setShowGrid(False)
		self.setAlternatingRowColors(True)
		self.setAutoScroll(True)
#		self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectItems)
		
		# Text
		self.setWordWrap(False)
		self.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
		
		# Selection Model
		self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QTableView.SelectionMode.ExtendedSelection)
		
		# Drag n Drop
		self.setDragEnabled(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
		self.setDragDropOverwriteMode(False)

		self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
		self.setDropIndicatorShown(True)
		
		self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		
		# Headers
		self.verticalHeader()  .setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.verticalHeader()  .hide()
		self.horizontalHeader().hide()

		# Scrolling
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

	@QtCore.Slot()
	def toggleColumnSelection(self):

		# NOTE: Unused?

		self.selectionModel().clearSelection() if self.selectionModel().hasSelection() else self.selectAll()

	@QtCore.Slot()
	def toggleSelectedVisibility(self):

		for row_index in self.selectionModel().selectedRows():
			pass
	
#			self.model().toggleBinColumnVisibiltyForIndex(row_index)
	###

	def setModel(self, model:QtCore.QAbstractItemModel):
		
		if self.model() == model:
			return

		super().setModel(model)

		# NOTE: Need better way to do this for model/delegate reassignments
		self.itemDelegate().sig_hide_column_index.connect(self.toggleBinColumnVisibility)
		self.itemDelegate().sig_remove_column_index.connect(self.removeUserColumn)
#		self.itemDelegate().sig_rename_column_for_index.connect(self.model().renameColumnForIndex)
		
		for col in range(model.columnCount(QtCore.QModelIndex())):

			editor_feature = model.headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

			if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
				self.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)

			else:
				self.horizontalHeader().setSectionResizeMode(col,QtWidgets.QHeaderView.ResizeMode.ResizeToContents)


	
	def itemDelegate(self) -> editordelegates.BSBinViewColumnDelegate:
		return super().itemDelegate()
	
	@QtCore.Slot(int, QtCore.QModelIndex)
	def toggleBinColumnVisibility(self, row:int, parent:QtCore.QModelIndex):

		if not self.model() or parent.isValid():
			return
		
		row_index = self.model().index(row, 1, QtCore.QModelIndex())
		is_hidden = row_index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
		self.model().setData(row_index, not is_hidden, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

	@QtCore.Slot(int, QtCore.QModelIndex)
	def removeUserColumn(self, row:int, parent:QtCore.QModelIndex):
		
		if not self.model() or parent.isValid():
			return
		
		self.model().removeRow(row, QtCore.QModelIndex())