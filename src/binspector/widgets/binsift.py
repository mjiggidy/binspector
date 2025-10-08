from PySide6 import QtWidgets
from ..views import treeview

class LBBinSiftSettingsView(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setContentsMargins(0,0,0,0)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)

		self._chk_sift_enabled = QtWidgets.QCheckBox("Sift Enabled")

		self._tree_siftsettings = treeview.LBTreeView()

		self.layout().addWidget(self._chk_sift_enabled)
		self.layout().addWidget(self._tree_siftsettings)