import typing
from PySide6 import QtCore

from ..binitems import binitemtypes
from ..models import viewmodels

class LBAbstractPresenter(QtCore.QObject):
	"""A general manager thing that also maintains a viewmodel of its data"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self._view_model = viewmodels.BSBinItemViewModel()
	
	def viewModel(self) -> viewmodels.BSBinItemViewModel:
		"""Return the internal view model"""
		return self._view_model
	
	def addRow(self, row_data:dict[str,binitemtypes.BSAbstractViewItem]):
		self.addRows([row_data])

	def addRows(self, row_data_list:list[dict[str,binitemtypes.BSAbstractViewItem]]):
		self._view_model.addBinItems(row_data_list)
	
	def addHeader(self, header_data:binitemtypes.BSAbstractViewHeaderItem):
		self._view_model.addHeader(header_data)
	
class LBItemDefinitionView(LBAbstractPresenter):
	"""A general data manager that maintains a key/val viewmodel of its data"""

	@QtCore.Slot(object)
	def addRow(self, row_data:dict[binitemtypes.BSAbstractViewHeaderItem|str,binitemtypes.BSAbstractViewItem|typing.Any], add_new_headers:bool=False):
		
		return self.addRows([row_data], add_new_headers)
	
	@QtCore.Slot(object)
	def addRows(self, row_data_list:list[dict[binitemtypes.BSAbstractViewHeaderItem|str,binitemtypes.BSAbstractViewItem|typing.Any]], add_new_headers:bool=False):
		#print("I HAVE HERE:", row_data_list)
		processed_row_list = []
		for row_data in row_data_list:

			processed_row = dict()

			for term, definition in row_data.items():
				term = self._buildViewHeader(term)
				if add_new_headers and term.field_name() not in self.viewModel().fields():
					self.addHeader(term)
				
				definition = self._buildViewItem(definition)
				processed_row[term.field_name()] = definition

			processed_row_list.append(processed_row)
		
		self._view_model.addBinItems(processed_row_list)
	
	def _buildViewHeader(self, term:typing.Any) -> binitemtypes.BSAbstractViewHeaderItem:
		if isinstance(term, binitemtypes.BSAbstractViewHeaderItem):
			return term
		return binitemtypes.BSAbstractViewHeaderItem(field_name=str(term), display_name=str(term).replace("_", " ").title())
	
	def _buildViewItem(self, definition:typing.Any) -> binitemtypes.BSAbstractViewItem:
		return binitemtypes.get_viewitem_for_item(definition)