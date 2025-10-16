from PySide6 import QtWidgets
from ..views import logtreeview

class BSLogViewerWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._tree_log = logtreeview.BSLogTreeView()
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().addWidget(self._tree_log)
	
	def treeView(self) -> logtreeview.BSLogTreeView:
		"""Get the treeview displaying the logs"""

		return self._tree_log