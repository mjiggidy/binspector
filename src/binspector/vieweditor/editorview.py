from PySide6 import QtWidgets, QtCore
from . import editorproxymodel, editordelegates

class BSBinViewColumnListView(QtWidgets.QTableView):
	"""A QTableView for bin view column data"""

	def __init__(self):

		super().__init__()

		self.setItemDelegate(editordelegates.BSBinViewColumnDelegate())
		
		# Background 'n' grid
		self.setShowGrid(False)
		self.setAlternatingRowColors(True)
		self.setAutoScroll(True)
		
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
		

		
		# Headers
		self.verticalHeader()  .setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.verticalHeader()  .hide()
		self.horizontalHeader().hide()

		# Scrolling
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

		# Model
		self.setModel(editorproxymodel.BSBinViewColumnEditorProxyModel())

	@QtCore.Slot()
	def toggleColumnSelection(self):

		# NOTE: Unused?

		self.selectionModel().clearSelection() if self.selectionModel().hasSelection() else self.selectAll()

	@QtCore.Slot()
	def toggleSelectedVisibility(self):

		for row_index in self.selectionModel().selectedRows():
	
			self.model().toggleBinColumnVisibiltyForIndex(row_index)
	###

	def setModel(self, model:editorproxymodel.BSBinViewColumnEditorProxyModel):
		
		if self.model() == model:
			return

		super().setModel(model)

		# NOTE: Need better way to do this for model/delegate reassignments
		self.itemDelegate().sig_hide_column_index.connect(self.model().toggleBinColumnVisibiltyForIndex)
		self.itemDelegate().sig_remove_column_index.connect(self.model().removeBinColumnForIndex)
		self.itemDelegate().sig_rename_column_for_index.connect(self.model().renameColumnForIndex)
		
		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		
		for col, feat in enumerate(model.features()):
			if feat == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
				self.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
	
	def model(self) -> editorproxymodel.BSBinViewColumnEditorProxyModel:
		"""This model returns a proxy model"""

		return super().model()
	
	def itemDelegate(self) -> editordelegates.BSBinViewColumnDelegate:
		return super().itemDelegate()
	
#	def setItemDelegate(self, delegate:editordelegates.BSBinViewColumnDelegate):
#		
#		if self.itemDelegate() == delegate:
#			return
#
#		delegate.sig_hide_column_index.connect(self.model().toggleBinColumnVisibiltyForIndex)
#		
#		super().setItemDelegate(delegate)