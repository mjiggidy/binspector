import logging

from PySide6 import QtWidgets, QtGui, QtCore

from ..binviewprovider import providermodel, binviewsources
from . import editorproxymodel, editorview
from ..binview import binviewmodel, binviewitemtypes
from ..widgets import binviewcombobox

class BSBinViewColumnEditor(QtWidgets.QWidget):

	sig_export_binview_requested = QtCore.Signal(object, str)
	"""Export the given binview"""

	sig_delete_binview_requested = QtCore.Signal(object)
	"""Delete the given binview"""

	def __init__(self, *args, bin_view_provider:providermodel.BSBinViewProviderModel|None=None, bin_view_model:binviewmodel.BSBinViewModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		# Bin View Name Display
		self._bin_view_provider       = None
		self._cmb_bin_view_list       = binviewcombobox.BSBinViewSelectorComboBox()

		self._btn_view_list_add       = QtWidgets.QPushButton()
		self._btn_view_list_delete    = QtWidgets.QPushButton()
		
		# Editor View
		self._view_editor = editorview.BSBinViewColumnListView()

		# Action Buttons
		self._btn_toggle_all = QtWidgets.QPushButton(self.tr("Toggle Visibility"))
		self._btn_add_col    = QtWidgets.QPushButton(self.tr("Add User Column"))


		self._lay_view_list = QtWidgets.QHBoxLayout()
		self._lay_view_list.setSpacing(0)

		self._lay_view_list.addWidget(self._cmb_bin_view_list)
		self._lay_view_list.addWidget(self._btn_view_list_add)
		self._lay_view_list.addWidget(self._btn_view_list_delete)

		self._cmb_bin_view_list.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self._cmb_bin_view_list.sizePolicy().verticalPolicy()))
		self._btn_view_list_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._btn_view_list_delete.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))

		self._btn_view_list_add.clicked.connect(self.requestExportBinView)
		self._btn_view_list_delete.clicked.connect(self.requestDeleteBinView)

		self.layout().addLayout(self._lay_view_list)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Add, Modify, and Rearrange Columns:")))
		self.layout().addWidget(self._view_editor)

		self._lay_buttons = QtWidgets.QHBoxLayout()


		self._lay_buttons.addWidget(self._btn_add_col)
		self._lay_buttons.addStretch()
		self._lay_buttons.addWidget(self._btn_toggle_all)

		self.layout().addLayout(self._lay_buttons)

		self._cmb_bin_view_list.currentTextChanged.connect(self.viewWasChanged)

		self._btn_toggle_all.clicked.connect(self._view_editor.toggleSelectedVisibility)
		self._btn_add_col.clicked.connect(self._view_editor.model().appendUserColumn)

		self.setBinViewModel   (bin_view_model    or binviewmodel.BSBinViewModel())
		self.setBinViewProvider(bin_view_provider or providermodel.BSBinViewProviderModel())

	def _setupComboBox(self):
		"""Set up the bin view selector"""

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):

		if self._view_editor.model().sourceModel() == bin_view_model:
			return
		
		logging.getLogger(__name__).debug("Setting editor model to %s", bin_view_model.binViewName())
		
		# NOTE: This was commented out and probably ruining my life but I don't remember why yet.  So hello, future me.
		self._view_editor.model().setSourceModel(bin_view_model)
	
	def setBinViewProvider(self, bin_view_provider:providermodel.BSBinViewProviderModel):

		if self._bin_view_provider == bin_view_provider:
			return
		
		if self._bin_view_provider is not None:
			self._bin_view_provider.disconnect(self)
		
		self._bin_view_provider = bin_view_provider

		self._cmb_bin_view_list.setModel(self._bin_view_provider)

	@QtCore.Slot()
	def viewWasChanged(self):
		"""Update buttons on view change"""

		binview_source:binviewsources.BSAbstractBinViewSource = self._cmb_bin_view_list.currentData()

		stored_names = iter(bvs.name() for bvs in self._bin_view_provider.storedBinViewSources())

		self._btn_view_list_delete.setEnabled(
			not binview_source.isModified() \
			and binview_source.name() in (bvs.name() for bvs in self._bin_view_provider.storedBinViewSources())
		)

	@QtCore.Slot()
	def requestExportBinView(self):
		"""Prepare binview as a dict for export"""

		binview_info = self._view_editor.model().sourceModel().binViewInfo()

		if binview_info is None:
			raise ValueError("No bin view to save")

		save_name = self._promptForBinViewName()

		if save_name:
			self.sig_export_binview_requested.emit(binview_info, save_name)

	@QtCore.Slot()
	def requestDeleteBinView(self):

		binview_source:binviewsources.BSAbstractBinViewSource = self._cmb_bin_view_list.currentData()

		if not binview_source:

			logging.getLogger(__name__).error("No bin view selected for deletion")
			return

		if QtWidgets.QMessageBox.question(
			self,
			self.tr("Delete Bin View"),
			self.tr("Are you sure you want to delete the stored bin view {binview_name}?").format_map({"binview_name":binview_source.name()})
		) != QtWidgets.QMessageBox.StandardButton.Yes:
			
			return
		
		self.sig_delete_binview_requested.emit(binview_source.name())
	
	def _promptForBinViewName(self) -> str|None:

		while True:

			# NOTE: Gonnanita validate that string

			# Ask for name
			save_name, was_serious_about_it = QtWidgets.QInputDialog.getText(
				self,
				self.tr("View Name"),
				self.tr("Name your view:"),
				text = self._cmb_bin_view_list.currentText()
			)

			if not was_serious_about_it:
				return None
			
			# Start over if overwrite is "undesirable" to the "user"
			if save_name in [bvs.name() for bvs in self._bin_view_provider.storedBinViewSources()]:

				user_choice = QtWidgets.QMessageBox.question(
					self,
					self.tr("Bin View Already Exists"),
					f"Replace the existing bin view named \"{save_name}\"?"
				)

				if user_choice == QtWidgets.QMessageBox.StandardButton.No:
					continue
			
			return save_name


	def binViewSelector(self) -> binviewcombobox.BSBinViewSelectorComboBox:

		return self._cmb_bin_view_list