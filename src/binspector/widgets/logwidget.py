from PySide6 import QtWidgets
from ..views import logtreeview

class BSLogViewerWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._tree_log = logtreeview.BSLogTreeView()

		self.layout().addWidget(self._tree_log)