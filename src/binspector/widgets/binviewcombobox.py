from PySide6 import QtCore, QtWidgets

from ..binviewprovider import providermodel, binviewsources

class BSBinViewSelectorComboBox(QtWidgets.QComboBox):
	"""A QComboBox for selecting binviews from a given binview provider"""

	sig_binview_source_selected = QtCore.Signal(object)
	"""The user selected a binview from the binview provider"""

	def __init__(self, *args, binview_provider:providermodel.BSBinViewProviderModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setModel(binview_provider or providermodel.BSBinViewProviderModel())

		self.activated.connect(self.userSelectedBinViewSource)

	def setModel(self, model:providermodel.BSBinViewProviderModel):
		
		if self.model() == model:
			return
		
		model.sig_session_sources_changed.connect(lambda: self.setCurrentIndex(0))

		super().setModel(model)
	
	@QtCore.Slot(int)
	def userSelectedBinViewSource(self, selected_index:int):


		selected_binview_source = self.currentData()

		self.sig_binview_source_selected.emit(selected_binview_source)