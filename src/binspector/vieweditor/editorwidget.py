import logging

from PySide6 import QtWidgets, QtGui, QtCore
from . import editorproxymodel, editorview
from ..binview import binviewmodel

class BSBinViewColumnEditor(QtWidgets.QWidget):

	def __init__(self, *args, bin_view_model:binviewmodel.BSBinViewModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		# Bin View Name Display
		self._cmb_bin_view_list       = QtWidgets.QComboBox()

		self._btn_view_list_add       = QtWidgets.QPushButton()
		self._btn_view_list_modify    = QtWidgets.QPushButton()
		self._btn_view_list_delete    = QtWidgets.QPushButton()
		
		# Editor View
		self._view_editor = editorview.BSBinViewColumnListView()

		# Action Buttons
		self._btn_toggle_all = QtWidgets.QPushButton(self.tr("Toggle Visibility"))
		self._btn_add_col    = QtWidgets.QPushButton(self.tr("Add User Column"))


		self._lay_view_list = QtWidgets.QHBoxLayout()
		self._lay_view_list.setSpacing(0)

		self._lay_view_list.addWidget(self._cmb_bin_view_list)
		self._lay_view_list.addWidget(self._btn_view_list_modify)
		self._lay_view_list.addWidget(self._btn_view_list_add)
		self._lay_view_list.addWidget(self._btn_view_list_delete)

		self._cmb_bin_view_list.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self._cmb_bin_view_list.sizePolicy().verticalPolicy()))
		self._btn_view_list_modify.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))
		self._btn_view_list_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._btn_view_list_delete.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
		self.layout().addLayout(self._lay_view_list)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Add, Modify, and Rearrange Columns:")))
		self.layout().addWidget(self._view_editor)

		self._lay_buttons = QtWidgets.QHBoxLayout()


		self._lay_buttons.addWidget(self._btn_add_col)
		self._lay_buttons.addStretch()
		self._lay_buttons.addWidget(self._btn_toggle_all)

		self.layout().addLayout(self._lay_buttons)

		self._btn_toggle_all.clicked.connect(self._view_editor.toggleSelectedVisibility)
		self._btn_add_col.clicked.connect(self._view_editor.model().appendUserColumn)

		self.setBinViewModel(bin_view_model or binviewmodel.BSBinViewModel())
		
	
	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):

		if self._view_editor.model().binViewModel() == bin_view_model:
			return

		if self._view_editor.model().binViewModel() is not None:
			self._view_editor.model().binViewModel().sig_bin_view_name_changed.disconnect(self._cmb_bin_view_list.addItem)
		
		logging.getLogger(__name__).debug("Setting editor model to %s", bin_view_model.binViewName())
		
		#bin_view_model.sig_bin_view_name_changed.connect(self._cmb_bin_view_list.addItem)
		self._view_editor.model().setSourceModel(bin_view_model)
		
		self._cmb_bin_view_list.addItem(bin_view_model._bin_view_name)
		self._cmb_bin_view_list.setCurrentText(bin_view_model._bin_view_name)
		
		
		