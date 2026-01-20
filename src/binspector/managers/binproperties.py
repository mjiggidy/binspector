import logging, typing
import avb, avbutils
from PySide6 import QtCore
from ..models import viewmodelitems, viewmodels
from ..core import binparser
from . import base

TEMP_POSITION_OFFSET_THING = 10

class BSBinViewModeManager(QtCore.QObject):
	"""Manage them viewmodes"""

	sig_view_mode_changed = QtCore.Signal(object)
	"""The view mode has been changed"""

	def __init__(self, initial_mode:avbutils.BinDisplayModes=avbutils.BinDisplayModes.LIST, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._current_mode = initial_mode

	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current bin view mode"""

		if view_mode != self._current_mode:
			self._current_mode = view_mode
			self.sig_view_mode_changed.emit(self._current_mode)
	
	def viewMode(self) -> avbutils.BinDisplayModes:
		return self._current_mode

class BSBinViewManager(base.LBItemDefinitionView):

	sig_bin_view_changed = QtCore.Signal(object, object, int, int)
	"""Binview has been reset"""

	sig_view_mode_toggled = QtCore.Signal(object)
	"""Binview has been toggled on/off"""

	sig_all_columns_toggled = QtCore.Signal(object)
	"""All columns have been toggled on/off (opposite of `sig_view_mode_toggled`)"""

	sig_bin_filters_toggled = QtCore.Signal(object)
	"""Filters have been toggled on/off"""

	sig_all_items_toggled = QtCore.Signal(object)
	"""All items have been toggled on/off (opposite of `sig_bin_filters_toggled`)"""

	sig_focus_bin_column    = QtCore.Signal(str)
	"""Focus a given bin column index"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._default_sort_columns:list[list[int,str]] = []

		self._binview_is_enabled = True
		self._filters_enabled    = True

		# Emit the opposites
		self.sig_view_mode_toggled  .connect(lambda bv_enabled: self.sig_all_columns_toggled.emit(not bv_enabled))
		self.sig_bin_filters_toggled.connect(lambda fl_enabled: self.sig_all_items_toggled  .emit(not fl_enabled))

		#self.sig_all_columns_toggled.connect(lambda all_columns: print(f"{all_columns=}")) #Not?
		#self.sig_all_items_toggled.connect(lambda all_visible: print(f"{all_visible=}")) # Firing

	@QtCore.Slot(object, object, object, object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict|None=None, frame_view_scale:int=avbutils.THUMB_FRAME_MODE_RANGE.start, script_view_scale:int=avbutils.THUMB_SCRIPT_MODE_RANGE.start):
		"""Set columns and their widths"""

		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order",  self.tr("Order")),
			viewmodelitems.LBAbstractViewHeaderItem("title",  self.tr("Title")),
			viewmodelitems.LBAbstractViewHeaderItem("format", self.tr("Format")),
			viewmodelitems.LBAbstractViewHeaderItem("type",   self.tr("Type")),
			viewmodelitems.LBAbstractViewHeaderItem("width",  self.tr("Width")),
			viewmodelitems.LBAbstractViewHeaderItem("hidden", self.tr("Is Hidden")),
		]
		
		for header in headers:
			super().addHeader(header)

		for idx, column in enumerate(bin_view.columns):
			column.update({
				"order": idx,
				"width": column_widths.get(column["title"],None)
			})
				
			self.addColumnDefinition(column)
		
		self.sig_bin_view_changed.emit(bin_view, column_widths, frame_view_scale, script_view_scale)

	@QtCore.Slot(object)
	def setDefaultSortColumns(self, sort_settings:list[list[int,str]]):

		self._default_sort_columns = sort_settings

	def defaultSortColumns(self) -> list[list[int,str]]:

		return self._default_sort_columns

	@QtCore.Slot(object)
	def addColumnDefinition(self, column_definition:dict[str,object]):

		column_definition["format"] = avbutils.BinColumnFormat(column_definition["format"])
		self.addRow(column_definition)
	
	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		if is_enabled != self._binview_is_enabled:

			self._binview_is_enabled = is_enabled
			self.sig_view_mode_toggled.emit(self._binview_is_enabled)
	
	@QtCore.Slot(object)
	def setAllColumnsVisible(self, all_visibile:bool):
		"""Convenience method: Opposite of setBinViewEnabled"""

		self.setBinViewEnabled(not all_visibile)

	@QtCore.Slot(object)
	def setBinFiltersEnabled(self, is_enabled:bool):

		if is_enabled != self._filters_enabled:

			self._filters_enabled = is_enabled
			self.sig_bin_filters_toggled.emit(self._filters_enabled)
	
	@QtCore.Slot(object)
	def setAllItemsVisible(self, all_visible:bool):

		self.setBinFiltersEnabled(not all_visible)

	@QtCore.Slot(QtCore.QModelIndex)
	def requestFocusColumn(self, selected_index:QtCore.QModelIndex):

		
		# Field name
		#clicked_row  = selected_index.row()
		header_names = [selected_index.model().headerData(i, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole) for i in range(selected_index.model().columnCount())]
		
		selected_format  = selected_index.siblingAtColumn(header_names.index("Type")).data(QtCore.Qt.ItemDataRole.UserRole).raw_data()
		selected_name    = selected_index.siblingAtColumn(header_names.index("Title")).data(QtCore.Qt.ItemDataRole.DisplayRole)
		
		logging.getLogger(__name__).debug("Requesting to focus bin view column %s: %s", selected_format, selected_name)

		selected_field_name = f"{selected_format}_{selected_name}" if selected_format == 40 else str(selected_format)

		#print(selected_field_name)

		
		#print(selected_index.data(QtCore.Qt.ItemDataRole.UserRole))
		self.sig_focus_bin_column.emit(selected_field_name)


class BSBinDisplaySettingsManager(base.LBItemDefinitionView):

	sig_bin_display_changed = QtCore.Signal(object)

	def __init__(self):

		super().__init__()

	@QtCore.Slot(object)
	def setBinDisplayFlags(self, bin_display:avbutils.BinDisplayItemTypes):

		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("name",  self.tr("Name")),
			viewmodelitems.LBAbstractViewHeaderItem("value", self.tr("Value")),
		]
		
		for header in headers:
			self.addHeader(header)
		
		for f in bin_display:
			self.addRow({"name": f.name, "value": f.value})
		
		self.sig_bin_display_changed.emit(bin_display)
		
class BSBinSortingPropertiesManager(base.LBItemDefinitionView):
	"""Bin sorting"""

	sig_bin_sorting_changed   = QtCore.Signal(object)

	@QtCore.Slot(object)
	def setBinSortingProperties(self, sorting:list[int,str]):
		
		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order",     self.tr("Order")),
			viewmodelitems.LBAbstractViewHeaderItem("direction", self.tr("Direction")),
			viewmodelitems.LBAbstractViewHeaderItem("column",    self.tr("Column"))
		]

		for header in headers:
			self.addHeader(header)
		
		for order, (direction, column_name) in enumerate(sorting):
			self.addRow({
				"order": order,
				"direction": QtCore.Qt.SortOrder(direction),
				"column": column_name
			})
		
		self.sig_bin_sorting_changed.emit([(QtCore.Qt.SortOrder(direction), column_name) for direction, column_name in sorting])

class BSBinSiftSettingsManager(base.LBItemDefinitionView):

	sig_sift_enabled          = QtCore.Signal(bool)
	sig_bin_view_changed      = QtCore.Signal(object)
	sig_sift_settings_changed = QtCore.Signal(object)

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):
		self.sig_bin_view_changed.emit(bin_view)


	@QtCore.Slot(bool, object)
	def setSiftSettings(self, sift_enabled:bool, sift_settings:list[avbutils.bins.BinSiftOption]):

		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="string", display_name=self.tr("String")))
		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="method", display_name=self.tr("Method")))
		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="column", display_name=self.tr("Column")))
		for idx, setting in enumerate(reversed(sift_settings)):
			self.addRow({
				"order": idx,
				"method": viewmodelitems.TRTEnumViewItem(setting.sift_method),
				"string": setting.sift_text,
				"column": setting.sift_column,
			})
		
		self.sig_sift_settings_changed.emit(sift_settings)		
		self.sig_sift_enabled.emit(sift_enabled)

class BSBinItemsManager(QtCore.QObject):
	
	sig_mob_added = QtCore.Signal(object)
	"""A mob was added to the bin items"""

	sig_mob_count_changed = QtCore.Signal(int)
	"""Mobs were added or removed"""

	sig_bin_view_changed = QtCore.Signal(object, object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._view_model = viewmodels.BSBinItemViewModel()

#		self._frame_scene = QtWidgets.QGraphicsScene()
		
		self._view_model.rowsInserted .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
		self._view_model.rowsRemoved  .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
		self._view_model.modelReset   .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))

	def viewModel(self) -> viewmodels.BSBinItemViewModel:
		"""Return the internal view model"""
		return self._view_model
	
	@QtCore.Slot(object)
	def addRow(self, row_data:dict[viewmodelitems.LBAbstractViewHeaderItem|str,viewmodelitems.LBAbstractViewItem|typing.Any], add_new_headers:bool=False):
		
		return self.addRows([row_data], add_new_headers)

	@QtCore.Slot(object)
	def addRows(self, row_data_list:list[dict[viewmodelitems.LBAbstractViewHeaderItem|str,viewmodelitems.LBAbstractViewItem|typing.Any]], add_new_headers:bool=False):
		#print("I HAVE HERE:", row_data_list)
		pass
	
	def addHeader(self, header_data:viewmodelitems.LBAbstractViewHeaderItem):
		self._view_model.addHeader(header_data)

	def _buildViewHeader(self, term:typing.Any) -> viewmodelitems.LBAbstractViewHeaderItem:
		if isinstance(term, viewmodelitems.LBAbstractViewHeaderItem):
			return term
		return viewmodelitems.LBAbstractViewHeaderItem(field_name=str(term), display_name=str(term).replace("_", " ").title())

	@QtCore.Slot(object, object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict[str,int]):

		self.viewModel().clear()

		for column in bin_view.columns:

			self.addHeader(
				viewmodelitems.LBAbstractViewHeaderItem(
					field_name="40_"+column["title"] if column["type"] == 40 else str(column["type"]),
					field_id=column["type"],
					format_id=column["format"],
					display_name=column["title"],
					is_hidden=column["hidden"],
					field_width=column_widths.get(column["title"])
				)
			)
		
		self.sig_bin_view_changed.emit(bin_view, column_widths)
	
	@QtCore.Slot(object)
	def addMob(self, mob_info:binparser.BinItemInfo):
		"""Add a single mob (convience method for `self.addMobs(mob_info_list:list[binparser.BinItemInfo])`)"""

		self.addMobs([mob_info])
		#self.sig_mob_added.emit(mob_info)
	
	@QtCore.Slot(object)
	def addMobs(self, mob_info_list:list[binparser.BinItemInfo]):
		"""Given a `list[binparser.BinItemInfo]` of parsed mobs, add their viewitems to the model"""

		# NOTE: ViewItems are currently determined in BinParser but then double-checked here
		# Figure out where to actually do that.  I think probably here instead.

		mobs_viewitems = []
		mobs_framepositions = []

		for mob_info in mob_info_list:

			mobs_framepositions.append(mob_info.frame_coordinates)

			mob_viewitems = dict()

			for field_id, mob_viewitem in mob_info.view_items.items():

				if field_id == 40 and isinstance(mob_viewitem, dict): # User column

					mob_viewitem = {
						str(user_col_name): viewmodelitems.get_viewitem_for_item(user_col_data)
						for user_col_name, user_col_data in mob_viewitem.items()
					}
				
				else:
					mob_viewitem = viewmodelitems.get_viewitem_for_item(mob_viewitem)
					
				mob_viewitems[field_id] = mob_viewitem

			mobs_viewitems.append(mob_viewitems)
		
		self._view_model.addBinItems(mobs_viewitems, mobs_framepositions)