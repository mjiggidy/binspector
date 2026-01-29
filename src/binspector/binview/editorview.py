from PySide6 import QtWidgets, QtCore
import binspector.binview.editordelegates as editordelegates

class BSBinViewColumnListView(QtWidgets.QTableView):

	def __init__(self):

		super().__init__()

		self.setItemDelegate(editordelegates.BSBinViewColumnDelegate())
		self.setShowGrid(False)
		self.setAlternatingRowColors(True)
		self.setWordWrap(False)
		self.setAutoScroll(True)
		
		self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QTableView.SelectionMode.ExtendedSelection)
		
		self.setDropIndicatorShown(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
		self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
		self.setDragEnabled(True)
		
		self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.verticalHeader().hide()
		self.horizontalHeader().hide()

		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)