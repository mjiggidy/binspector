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
		self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
		self.setDropIndicatorShown(True)
		
		# Headers
		self.verticalHeader()  .setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
		self.verticalHeader()  .hide()
		self.horizontalHeader().hide()

		# Scrolling
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

		# Model
		self.setModel(editorproxymodel.BSBinViewColumnEditorProxyModel())
	
	def model(self) -> editorproxymodel.BSBinViewColumnEditorProxyModel:
		"""This model returns a proxy model"""
		
		return super().model()
