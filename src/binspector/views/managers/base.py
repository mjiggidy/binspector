import typing
from PySide6 import QtCore
from ...models import viewmodels, viewmodelitems

class LBAbstractPresenter(QtCore.QObject):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self._view_model = viewmodels.TRTTimelineViewModel()
	
	def viewModel(self) -> viewmodels.TRTTimelineViewModel:
		"""Return the internal view model"""
		return self._view_model
	
	def addRow(self, row_data:dict[str,viewmodelitems.TRTAbstractViewItem]):
		self._view_model.addTimeline(row_data)
	
	def addHeader(self, header_data:viewmodelitems.TRTAbstractViewHeaderItem):
		self._view_model.addHeader(header_data)
	

class LBItemDefinitionView(LBAbstractPresenter):

	@QtCore.Slot(object)
	def addRow(self, row_data:dict[viewmodelitems.TRTAbstractViewHeaderItem|str,viewmodelitems.TRTAbstractViewItem|typing.Any], add_new_headers:bool=False):
		processed_row = dict()

		for term, definition in row_data.items():
			term = self._buildViewHeader(term)
			if add_new_headers and term.field_name() not in self.viewModel().fields():
				self.addHeader(term)
			
			definition = self._buildViewItem(definition)
			processed_row[term.field_name()] = definition

		return super().addRow(processed_row)
	
	def _buildViewHeader(self, term:typing.Any) -> viewmodelitems.TRTAbstractViewHeaderItem:
		if isinstance(term, viewmodelitems.TRTAbstractViewHeaderItem):
			return term
		return viewmodelitems.TRTAbstractViewHeaderItem(field_name=str(term), display_name=str(term).replace("_", " ").title())
	
	def _buildViewItem(self, definition:typing.Any) -> viewmodelitems.TRTAbstractViewItem:
		return viewmodelitems.get_viewitem_for_item(definition)