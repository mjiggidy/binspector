from PySide6 import QtWidgets
from . import treeview
from ..models import logmodels

class BSLogTreeView(treeview.BSTreeViewBase):
	"""A TreeView for viewin' trees. And logs.  Logs from trees."""

	def __init__(self, log_model:logmodels.BSLogDataModel|None=None, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		self.setAutoScroll(False)
		
		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		
		if log_model:
			self.setModel(log_model)