"""
The big fella
"""

import logging
import avb, avbutils

from PySide6 import QtCore, QtGui, QtWidgets

from . import proxystyles, scrollwidgets, widgetbars, binitems

from ..listview import listview
from ..frameview import frameview
from ..scriptview import scriptview

from ..models import viewmodels
from ..widgets import buttons
from . import delegate_lookup

from ..core.config import BSListViewConfig, BSFrameViewConfig, BSScriptViewConfig


class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_view_mode_changed   = QtCore.Signal(object)
	sig_bin_palette_changed = QtCore.Signal(QtGui.QPalette)
	sig_bin_font_changed    = QtCore.Signal(QtGui.QFont)
	sig_bin_model_changed   = QtCore.Signal(object)
	sig_focus_set_on_column = QtCore.Signal(int)	# Logical column index
	sig_bin_stats_updated   = QtCore.Signal(str)

	def __init__(self, *args, bin_model:viewmodels.BSBinItemViewModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)
		
		self._bin_model         = bin_model or viewmodels.BSBinItemViewModel()
		self._bin_filter_model  = viewmodels.BSBinViewProxyModel()
		self._selection_model   = QtCore.QItemSelectionModel(self._bin_filter_model, parent=self)
		#self._selection_syncer  = syncselection.BSSelectionSyncer(parent=self, selection_model=self._selection_model)
		
		#self._scene_frame       = QtWidgets.QGraphicsScene()

		# Save initial palette for later togglin'
		self._default_palette   = self.palette()
		self._bin_palette       = self.palette()
		self._default_font      = self.font()
		self._bin_font          = self.font()
		self._use_bin_appearance= True

		self._section_top       = widgetbars.BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		
		self._binitems_list     = listview.BSBinListView()
		self._binitems_frame    = frameview.BSBinFrameView()
		self._binitems_script   = scriptview.BSBinScriptView()

		self._binstats_list     = scrollwidgets.BSBinStatsLabel()
		self._binstats_frame    = scrollwidgets.BSBinStatsLabel()

		self._default_delegate_list   = binitems.BSGenericItemDelegate()
		self._default_delegate_script = binitems.BSGenericItemDelegate()

		# Create proxy style from application style for potential horizontal scrollbar height mods
		self._proxystyle_hscroll = proxystyles.BSScrollBarStyle(parent=self)

		self._setupWidgets()
		self._setupSignals()
		self._setupActions()
		
		self._setupBinModel()

	def _setupWidgets(self):

		# Top Tool Bar
		self._section_top._sld_frame_scale .setRange(BSFrameViewConfig.DEFAULT_FRAME_ZOOM_RANGE.start,   BSFrameViewConfig.DEFAULT_FRAME_ZOOM_RANGE.stop)
		self._section_top._sld_script_scale.setRange(BSScriptViewConfig.DEFAULT_SCRIPT_ZOOM_RANGE.start, BSScriptViewConfig.DEFAULT_SCRIPT_ZOOM_RANGE.stop)

		self.layout().addWidget(self._section_top)

		# Main List, Frame, and Script views
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._binitems_list)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._binitems_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._binitems_script)

		self._binitems_frame.setZoomRange(BSFrameViewConfig.DEFAULT_FRAME_ZOOM_RANGE)
		self._binitems_frame.setZoom(BSFrameViewConfig.DEFAULT_FRAME_ZOOM_START)
		
		self.layout().addWidget(self._section_main)

		self._binitems_list.setModel(self._bin_filter_model)
		self._binitems_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

		self._binitems_script.setModel(self._bin_filter_model)
		self._binitems_script.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		
		# NOTE: Set AFTER `view.setModel()`.  Got me good.
		self._binitems_list.setSelectionModel(self._selection_model)
		self._binitems_script.setSelectionModel(self._selection_model)
		
		# Adjust scrollbar height for macOS rounded corner junk
		self._binitems_list  .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

		self._binitems_list .addScrollBarWidget(self._binstats_list,  QtCore.Qt.AlignmentFlag.AlignLeft)
		self._binitems_frame.addScrollBarWidget(self._binstats_frame, QtCore.Qt.AlignmentFlag.AlignLeft)

	def _setupSignals(self):
		
		self._bin_filter_model.rowsInserted  .connect(self.updateBinStats)
		self._bin_filter_model.rowsRemoved   .connect(self.updateBinStats)
		self._bin_filter_model.modelReset    .connect(self.updateBinStats)
		self._bin_filter_model.layoutChanged .connect(self.updateBinStats)

		# NEW: Moving out from list view
		self._bin_filter_model.columnsInserted.connect(
			lambda parent_index, source_start, source_end:
			self.assignItemDelegates(parent_index, source_start)
		)
		self._bin_filter_model.columnsMoved.connect(
			lambda source_parent,
				source_logical_start,
				source_logical_end,
				destination_parent,
				destination_logical_start: # NOTE: Won't work for heirarchical models
			self.assignItemDelegates(destination_parent, min(source_logical_start, destination_logical_start))
		)

		self._section_top.sig_frame_scale_changed  .connect(self._binitems_frame.setZoom)
		self._binitems_frame.sig_zoom_level_changed.connect(self._section_top._sld_frame_scale.setValue)
		self._binitems_frame.sig_zoom_range_changed.connect(lambda r: self._section_top._sld_frame_scale.setRange(r.start, r.stop))

		self._section_top.sig_script_scale_changed         .connect(self._binitems_script.setFrameScale)
		self._binitems_script.sig_frame_scale_changed      .connect(self._section_top._sld_script_scale.setValue)
		self._binitems_script.sig_frame_scale_range_changed.connect(lambda r: self._section_top._sld_script_scale.setRange(r.start, r.stop))

		self.sig_bin_stats_updated.connect(self._binstats_list.setText)
		self.sig_bin_stats_updated.connect(self._binstats_frame.setText)

		#self._binitems_frame.scene().sig_bin_item_selection_changed.connect(self.setSelectedItems)

		#self._section_main.currentChanged.connect(self._selection_syncer.viewModeChanged)
		#self._selection_syncer.sig_frame_selection_changed.connect(print)

	def _setupActions(self):

		self._act_set_view_width_for_columns = QtGui.QAction(self._binitems_list)
		self._act_set_view_width_for_columns.setText(self.tr("Fit bin list columns to contents"))
		self._act_set_view_width_for_columns.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_T))
		self._act_set_view_width_for_columns.triggered.connect(lambda: self._binitems_list.setColumnWidthsFromBinView(QtCore.QModelIndex(), 0, self._binitems_list.header().count()-1))

		self._act_autofit_columns = QtGui.QAction(self._binitems_list)
		self._act_autofit_columns.setText(self.tr("Auto-fit bin list columns to contents"))
		self._act_autofit_columns.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.Key.Key_T))
		self._act_autofit_columns.triggered.connect(self._binitems_list.resizeAllColumnsToContents)
		
		self._binitems_list.addAction(self._act_set_view_width_for_columns)
		self._binitems_list.addAction(self._act_autofit_columns)

	@QtCore.Slot(QtCore.QModelIndex, int)
	def assignItemDelegates(self, parent_index:QtCore.QModelIndex, start_col_logical:int):

		if parent_index.isValid():
			logging.getLogger(__name__).error("Seems to be a child row? Weird. %s", str(parent_index))
			return
		
		# List View
		
		# Start by getting the leftmost visual index
		start_col_visual = self._binitems_list.header().visualIndex(start_col_logical)
		
		# For each col appearing visually after the start, map it to logical and assign its stuff
		for col_visual in range(start_col_visual, self._binitems_list.header().count()):

			col_logical = self._binitems_list.header().logicalIndex(col_visual)

			col_id = self._bin_filter_model.headerData(
				col_logical,
				QtCore.Qt.Orientation.Horizontal,
				viewmodels.viewmodelitems.BSBinColumnDataRoles.BSColumnID
			)

			col_format = self._bin_filter_model.headerData(
				col_logical,
				QtCore.Qt.Orientation.Horizontal,
				viewmodels.viewmodelitems.BSBinColumnDataRoles.BSDataFormat
			)

			# Do specific column IDs first
			if col_id in delegate_lookup.ITEM_DELEGATES_PER_FIELD_ID:
				col_delegate = delegate_lookup.ITEM_DELEGATES_PER_FIELD_ID[col_id]( padding=BSListViewConfig.DEFAULT_ITEM_PADDING)
				

			elif col_format in delegate_lookup.ITEM_DELEGATES_PER_FORMAT_ID:
				col_delegate = delegate_lookup.ITEM_DELEGATES_PER_FORMAT_ID[col_format]( padding=BSListViewConfig.DEFAULT_ITEM_PADDING)

			else:
				col_delegate = self._binitems_list.itemDelegate()
			
			# LOL: Just default for now
			
			
			#self._default_delegate_list.setItemPadding(BSListViewConfig.DEFAULT_ITEM_PADDING)
			
			
			self._binitems_list.setItemDelegateForColumn(col_logical, self._default_delegate_list)
			self._binitems_script.setItemDelegateForColumn(col_logical, self._default_delegate_script)


			


	@QtCore.Slot(object)
	def setBinModel(self, bin_model:viewmodels.BSBinItemViewModel):
		"""Set the bin item model for the bin"""

		if self._bin_model == bin_model:
			return
		
		self._bin_model = bin_model
		self._setupBinModel()
		
		logging.getLogger(__name__).debug("Set bin model=%s", self._bin_model)
		self.sig_bin_model_changed.emit(bin_model)
	
	def binModel(self) -> viewmodels.BSBinItemViewModel:
		return self._bin_model
	
	def _setupBinModel(self):
		"""Connect bin model to all the schtuff"""

		self._bin_filter_model.setSourceModel(self._bin_model)
		self._binitems_frame.scene().setBinFilterModel(self._bin_filter_model) # TODO: Don't need to set each time? CHECK

	###
	# View Mode Widgets
	###

	def listView(self) -> listview.BSBinListView:
		"""List View Mode widget"""

		return self._binitems_list
	
	def frameView(self) -> frameview.BSBinFrameView:
		"""Frame View Mode widget"""

		return self._binitems_frame

	def scriptView(self) -> scriptview.BSBinScriptView:
		"""Script View Mode widget"""
		
		return self._binitems_script
	
	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current bin view mode"""

		logging.getLogger(__name__).debug("Setting bin view mode to %s", str(view_mode))

		old_view_mode = avbutils.bins.BinDisplayModes(self._section_main.currentIndex())

		self._section_main.setCurrentIndex(int(view_mode))
		self._section_top .setViewMode(view_mode)

		# Sync selection from old view to new view

		if view_mode == avbutils.bins.BinDisplayModes.FRAME:
			self._binitems_frame.scene().setSelectedItems(
				list(x.row() for x in self._selection_model.selectedRows())
			)

		elif view_mode == avbutils.bins.BinDisplayModes.SCRIPT:

			list_headers = self._binitems_list.header().saveState()
			self._binitems_script.header().restoreState(list_headers)
			self._binitems_script.applyHeaderConstraints()

		elif old_view_mode == avbutils.bins.BinDisplayModes.FRAME:

			self._selection_model.clearSelection()

			for row, item in enumerate(self._binitems_frame.scene()._bin_items):
				if item.isSelected():

					self._selection_model.select(
						self._bin_filter_model.index(row, 0, QtCore.QModelIndex()),
						QtCore.QItemSelectionModel.SelectionFlag.Select|QtCore.QItemSelectionModel.SelectionFlag.Rows
					)

		self.sig_view_mode_changed.emit(view_mode)

	def viewMode(self) -> avbutils.BinDisplayModes:
		"""Current view mode"""

		return avbutils.BinDisplayModes(self._section_main.currentIndex())
	
#	def setListView(self, treeview:bintreeview.BSBinTreeView):
#
#		self._binitems_list = treeview
#		self._setViewModeWidget(avbutils.BinDisplayModes.LIST, self._binitems_list)

	
#	def setFrameView(self, frame_view:binframeview.BSBinFrameView):
#
#		self._binitems_frame = frame_view
#		self._setViewModeWidget(avbutils.BinDisplayModes.FRAME, self._binitems_frame)

	
#	def setScriptView(self, script_view:binscriptview.BSBinScriptView):
#
#		self._binitems_script = script_view
#		self._setViewModeWidget(avbutils.BinDisplayModes.SCRIPT, self._binitems_script)

	
#	def setTopWidgetBar(self, toolbar:widgetbars.BSBinContentsTopWidgetBar):
#		self._section_top = toolbar	

#	@QtCore.Slot(object)
#	def setBinAppearanceEnabled(self, is_enabled:bool):
#		
#		self._use_bin_appearance = is_enabled
#		self.setPalette(self._bin_palette if is_enabled else self._default_palette)
#		self.setFont(self._bin_font if is_enabled else self._default_font)
#
#	@QtCore.Slot(object)
#	def setUseSystemAppearance(self, use_system:bool):
#
#		self.setBinAppearanceEnabled(not use_system)

	###
	# Bin Views and Filters
	###

	@QtCore.Slot(object, object, int, int)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict[str,int], frame_scale:int, script_scale:int):

		self.setBinViewName(bin_view.name)
		self.frameView().setZoom(frame_scale)
		self.frameView().ensureVisible(0, 0, 50, 50, 4,2)
		
		self.scriptView().setFrameScale(script_scale)

		#print("Okay haha...")

		for col in range(self.listView().header().count()):
			self.listView().setColumnWidthFromBinView(col, True)

	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		# TODO: Do I need to emit a confirmation signal here?
		self._bin_filter_model.setBinViewEnabled(is_enabled)

	@QtCore.Slot(object)
	def setBinViewName(self, bin_view_name:str):
		"""Set the name of the current bin view"""

		# TODO: Faking this for now, will need a model I guess
		if bin_view_name not in (
			self.topWidgetBar().binViewSelector().itemText(idx)
			for idx in range(self.topWidgetBar().binViewSelector().count())
		):
			self.topWidgetBar().binViewSelector().addItem(bin_view_name)

		self.topWidgetBar().binViewSelector().setItemText(0, bin_view_name)
		self.topWidgetBar().binViewSelector().setCurrentIndex(0)
	
	@QtCore.Slot(object)
	def setBinFiltersEnabled(self, is_enabled:bool):

		self._bin_filter_model.setBinFiltersEnabled(is_enabled)

	@QtCore.Slot(bool)
	def setSiftEnabled(self, is_enabled:bool):

		self._bin_filter_model.setSiftEnabled(is_enabled)

	@QtCore.Slot(object)
	def setSiftOptions(self, sift_options:avbutils.bins.BinSiftOption):

		self._bin_filter_model.setSiftOptions(sift_options)

#	@QtCore.Slot(object)
#	def setDisplayMode(self, mode:avbutils.BinDisplayModes):
#		pass

	###
	# Bin Appearance
	###

	@QtCore.Slot(QtGui.QPalette)
	def setBinPalette(self, palette:QtGui.QPalette):
		"""Set the color palette for the bin"""

		if self._bin_palette == palette:
			return
		
		self.setPalette(palette)
		self._bin_palette = palette
		self.sig_bin_palette_changed.emit(palette)
	
	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, bin_font:QtGui.QFont):
		"""Set the font for the bin"""
		
		if self._bin_font == bin_font:
			return
		
		self._bin_font = bin_font # TODO: Neeeded?
		
		self._binitems_list   .setFont(bin_font)
		self._binitems_frame  .setFont(bin_font)
		self._binitems_script .setFont(bin_font)
		
		self.sig_bin_font_changed.emit(bin_font)

	###
	# Misc
	###

	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		"""Set list item padding"""

		self._default_delegate_list.setItemPadding(padding)
		logging.getLogger(__name__).error("Padding %s", str(padding))
		self._binitems_script.setItemPadding(padding)

	@QtCore.Slot(str)
	def focusBinColumn(self, focus_field_name:str) -> bool:

		for log_idx, field_name in enumerate(
			[self._binitems_list.model().headerData(i, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+5)
			for i in range(self._binitems_list.header().count())]
			):

			#print(log_idx, field_name)

			if field_name == focus_field_name:
				#print("GOT IT AT", log_idx)
				self._section_main.currentWidget().setFocus()
				self._binitems_list.selectSection(log_idx)
				self._binitems_list.scrollTo(self._binitems_list.model().index(0, log_idx, QtCore.QModelIndex()), QtWidgets.QTreeView.ScrollHint.PositionAtCenter)
				
				
				self.sig_focus_set_on_column.emit(log_idx)
				return True
		
		QtWidgets.QApplication.beep()
		#self.sig_focus_set_on_column.emit(-1)
		
		return False

	###
	# Scrollbar widgets
	###

	def addScrollBarWidget(self, widget:QtWidgets.QWidget, view_mode:avbutils.bins.BinDisplayModes):

		scroll_area:QtWidgets.QScrollArea = self._section_main.widget(view_mode).scrollArea()

		scroll_area.addScrollBarWidget(widget, QtCore.Qt.AlignmentFlag.AlignLeft)

		widget.setFixedWidth(
			self._proxystyle_hscroll.pixelMetric(
				QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent
			)
		)
	
	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setBottomScrollbarScaleFactor(self, scale_factor:int|float):

		self._proxystyle_hscroll.setScrollbarScaleFactor(scale_factor)

		# .update()/.polish() doesn't work. Need to re-set each time?
		self._binitems_list  .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)
	
	def scrollbarScaler(self) -> proxystyles.BSScrollBarStyle:
		"""The scaler for the horizontal scroll bar"""

		return self._proxystyle_hscroll
	
	def topWidgetBar(self) -> widgetbars.BSBinContentsTopWidgetBar:
		return self._section_top

	@QtCore.Slot()
	def updateBinStats(self):

		count_visible = self._bin_filter_model.rowCount()
		count_all     = self._bin_filter_model.sourceModel().rowCount()

		info_text = self.tr("Showing {current_item_count} of {total_item_count} items").format(
			current_item_count=QtCore.QLocale.system().toString(count_visible),
			total_item_count=QtCore.QLocale.system().toString(count_all)
		)
		
		self.sig_bin_stats_updated.emit(info_text)