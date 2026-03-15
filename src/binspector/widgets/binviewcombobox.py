from PySide6 import QtCore, QtWidgets

from ..binview import binviewsprovider, binviewsources

class BSBinViewSelectorComboBox(QtWidgets.QComboBox):
	"""A QComboBox for selecting binviews from a given binview provider"""

	sig_binview_selected = QtCore.Signal(object)
	"""The user selected a binview from the binview provider"""

	def __init__(self, *args, binview_provider:binviewsprovider.BSBinViewProviderModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setModel(binview_provider or binviewsprovider.BSBinViewProviderModel())

		self.activated.connect(self.userSelectedBinView)

	def setModel(self, model:binviewsprovider.BSBinViewProviderModel):
		
		if self.model() == model:
			return
		
		model.sig_session_sources_changed.connect(lambda: self.setCurrentIndex(0))

		super().setModel(model)
	
	@QtCore.Slot(int)
	def userSelectedBinView(self, selected_index:int):

		model_index   = self.model().index(selected_index, 0, QtCore.QModelIndex())
		binview_source:binviewsources.BSAbstractBinViewSource = model_index.data(QtCore.Qt.ItemDataRole.UserRole)
		
		print("User selected ", binview_source.name())
		self.sig_binview_selected.emit(binview_source.binViewInfo())