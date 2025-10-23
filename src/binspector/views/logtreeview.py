from PySide6 import QtWidgets
from ..models import logmodels

class BSLogTreeView(QtWidgets.QTreeView):
	"""A TreeView for viewin' trees. And logs.  Logs from trees."""

	def __init__(self, log_model:logmodels.BSLogDataModel, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		
		self.setModel(log_model)