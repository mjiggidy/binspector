from PySide6 import QtWidgets, QtGui, QtCore
from . import editorview, editormodel

class BSBinViewColumnEditor(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		self._cmb_bin_view_list       = QtWidgets.QComboBox()
		self._btn_view_list_add       = QtWidgets.QPushButton()
		self._btn_view_list_modify = QtWidgets.QPushButton()
		self._btn_view_list_delete     = QtWidgets.QPushButton()
		
		self._view_editor = editorview.BSBinViewColumnListView()

		self._lay_view_list = QtWidgets.QHBoxLayout()
		self._lay_view_list.setSpacing(0)

		self._lay_view_list.addWidget(self._cmb_bin_view_list)
		self._lay_view_list.addWidget(self._btn_view_list_modify)
		self._lay_view_list.addWidget(self._btn_view_list_add)
		self._lay_view_list.addWidget(self._btn_view_list_delete)

		btn_width = 16*2
		self._cmb_bin_view_list.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self._cmb_bin_view_list.sizePolicy().verticalPolicy()))
		self._btn_view_list_modify.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))
		self._btn_view_list_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._btn_view_list_delete.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
		self.layout().addLayout(self._lay_view_list)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Add, Modify, and Rearrange Columns:")))
		self.layout().addWidget(self._view_editor)

		self._lay_buttons = QtWidgets.QHBoxLayout()

		self._btn_toggle_all = QtWidgets.QPushButton(self.tr("Show All/None"))
		self._btn_add_col    = QtWidgets.QPushButton(self.tr("Add User Column"))

		self._lay_buttons.addWidget(self._btn_add_col)
		self._lay_buttons.addStretch()
		self._lay_buttons.addWidget(self._btn_toggle_all)

		self.layout().addLayout(self._lay_buttons)
	
	def setBinViewModel(self, bin_view_model:editorview.BSBinViewColumnListView):

		if self._view_editor.model() == bin_view_model:
			return
		
		print("Adding bin view", bin_view_model.binViewName())

		bin_view_model.sig_bin_view_name_changed.connect(self._cmb_bin_view_list.addItem)
		self._cmb_bin_view_list.addItem(bin_view_model.binViewName())
		self._view_editor.setModel(bin_view_model)

		for col in range(self._view_editor.horizontalHeader().count()):

			column_type = self._view_editor.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

			#print(column_type)
			
			if column_type == editormodel.BSBinViewColumnEditorColumns.NameColumn:
			#	print(f"Set {column_type} to {QtWidgets.QHeaderView.ResizeMode.Stretch}")
				self._view_editor.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
			
			else:
			#	print(f"Set {column_type} to {QtWidgets.QHeaderView.ResizeMode.ResizeToContents}")
				self._view_editor.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
	
