"""
The big fella
"""

import logging, typing
import avb, avbutils

from PySide6 import QtCore, QtGui, QtWidgets
from binspector.textview import textviewproxymodel

from ..core import icon_registry

from . import proxystyles, scrollwidgets, widgetbars

from ..textview import bincompositemodel, textview
from ..frameview import frameview
from ..scriptview import scriptview, scriptproxy

from ..binview import binviewitemtypes, binviewmodel
from ..binitems import binitemtypes, binitemsmodel
from ..binfilters import bindisplayproxymodel, binviewproxymodel, binfindproxymodel, binsiftproxymodel

from ..core.config import BSTextViewModeConfig, BSFrameViewModeConfig, BSScriptViewModeConfig

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_view_mode_changed      = QtCore.Signal(object)
	sig_bin_palette_changed    = QtCore.Signal(QtGui.QPalette)
	sig_bin_font_changed       = QtCore.Signal(QtGui.QFont)
	sig_bin_model_changed      = QtCore.Signal(object)
	sig_focus_set_on_column    = QtCore.Signal(int)	# Logical column index
	sig_bin_stats_updated      = QtCore.Signal(str)
	sig_bin_view_enabled       = QtCore.Signal(bool)
#	sig_bin_view_model_changed = QtCore.Signal(object)
	sig_bin_view_enabled       = QtCore.Signal(bool)

	def __init__(self, *args, bin_items_model:binitemsmodel.BSBinItemModel, bin_view_model:binviewmodel.BSBinViewModel, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)
		
		
		# Gaze upon these data models!  Very professional!

		self._bin_items_model  = bin_items_model
		self._bin_items_filter = bindisplayproxymodel.BSBinDisplayFilterProxyModel(bin_items_model=self._bin_items_model, parent=self)
		
		self._bin_view_model   = bin_view_model
		self._bin_view_filter  = binviewproxymodel.BSBinViewFilterProxyModel(bin_columns_model=self._bin_view_model, parent=self)

		self._bin_composite_model = bincompositemodel.BSBinCompositeModel(item_model=self._bin_items_filter, view_model=self._bin_view_filter, parent=self)

		self._bin_sift_filter = binsiftproxymodel.BSBinSiftFilterProxyModel(parent=self)	# TODO
		self._bin_sift_filter.setSourceModel(self._bin_composite_model)

		self._bin_find_filter = binfindproxymodel.BSFindInBinProxyModel(parent=self)
		self._bin_find_filter.setSourceModel(self._bin_sift_filter)

		self._bin_model_final = QtCore.QIdentityProxyModel(parent=self)
		self._bin_model_final.setSourceModel(self._bin_find_filter)

		self._test_scriptmodel = scriptproxy.BSScriptViewProxyModel()
		self._test_scriptmodel.setSourceModel(self._bin_model_final)

#		self._bin_filter_model_deprecated    = textviewproxymodel.BSBTextViewSortFilterProxyModelDEPRECATED(text_view_model=self._bin_composite_model)
		self._selection_model     = QtCore.QItemSelectionModel(self._bin_model_final, parent=self)

		# Save initial palette for later togglin'
		self._default_palette   = self.palette()
		self._bin_palette       = self.palette()
		self._default_font      = self.font()
		self._bin_font          = self.font()
		
		self._use_bin_appearance    = True
		self._use_bin_column_widths = BSTextViewModeConfig.USE_BIN_COLUMN_WIDTHS

		self._section_top       = widgetbars.BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		
		# Main View Mode Widgets
		self._viewmode_text     = textview.BSBinTextView()
		self._viewmode_frame    = frameview.BSBinFrameView()
		self._viewmode_script   = scriptview.BSBinScriptViewNEWGOOD()

		# Footers
		self._binstats_text = scrollwidgets.BSBinStatsLabel(
			filter_model       = self._bin_model_final,
			source_items_model = self._bin_items_model,
			source_cols_model  = self._bin_view_model
		)
		self._binstats_frame = scrollwidgets.BSBinStatsLabel(
			filter_model       = self._bin_model_final,
			source_items_model = self._bin_items_model,
			source_cols_model  = self._bin_view_model,
			stat_strings       = [self.tr("Showing {filtered_item_count} of {source_item_count} items")]
		)

		# Create proxy style from application style for potential horizontal scrollbar height mods
		self._proxystyle_hscroll = proxystyles.BSScrollBarStyle(parent=self)

		self._setupWidgets()

		self._setupTextViewMode()
		self._setupFrameViewMode()
		self._setupScriptViewMode()

		self._setupSignals()
#		self._setupActions()
		
#		self._setupBinModel()

	def _setupWidgets(self):

		# Top Tool Bar
		self._section_top._sld_frame_scale .setRange(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE.start,   BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE.stop)
		self._section_top._sld_script_scale.setRange(BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_RANGE.start, BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_RANGE.stop)

		self.layout().addWidget(self._section_top)

		# Main Text, Frame, and Script views
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._viewmode_text)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._viewmode_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._viewmode_script)
		
		self.layout().addWidget(self._section_main)

	def _setupTextViewMode(self):
		

		# Models
		self._viewmode_text.setModel(self._bin_model_final)
		self._viewmode_text.setSelectionModel(self._selection_model) # NOTE: Call after setModel()
		
		# Delegates
		self._viewmode_text.setBinItemIconRegistry(icon_registry.BIN_ITEM_TYPE_ICON_REGISTRY)

		# Scroll bars
		self._viewmode_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._viewmode_text.horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_text.addScrollBarWidget(self._binstats_text,  QtCore.Qt.AlignmentFlag.AlignLeft)

		# Signals
		self._viewmode_text.sig_hide_column_requested.connect(self.hideBinColumn)

	def _setupFrameViewMode(self):

		# Scene from model
		bin_frame_scene     = frameview.BSBinFrameScene(
			bin_filter_model = self._bin_model_final,
			brushes_manager  = frameview.painters.BSFrameItemBrushManager(parent=self._viewmode_frame),
		)
		self._viewmode_frame.setScene(bin_frame_scene)

		# Initial settings sync
		self._viewmode_frame.setZoomRange(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE)
		self._viewmode_frame.setZoom(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_START)

		# Scroll bars
		self._viewmode_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_frame.addScrollBarWidget(self._binstats_frame, QtCore.Qt.AlignmentFlag.AlignLeft)
		
		# Signals
		self._viewmode_frame.sig_zoom_level_changed.connect(self._section_top._sld_frame_scale.setValue)
		self._viewmode_frame.sig_zoom_range_changed.connect(lambda r: self._section_top._sld_frame_scale.setRange(r.start, r.stop))

	def _setupScriptViewMode(self):

		# Models
		self._viewmode_script.setModel(self._test_scriptmodel)
#		self._viewmode_script.setSelectionModel(self._selection_model)

		# Delegates
		self._viewmode_script.setBinItemIconRegistry(icon_registry.BIN_ITEM_TYPE_ICON_REGISTRY)
		
		# Scroll bars
		self._viewmode_script.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._viewmode_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

		# Signals
		self._viewmode_script.sig_frame_scale_changed      .connect(self._section_top._sld_script_scale.setValue)
#		self._viewmode_script.sig_frame_scale_range_changed.connect(lambda r: self._section_top._sld_script_scale.setRange(r.start, r.stop))
		self._viewmode_script.sig_hide_column_requested .connect(self.hideBinColumn)



	def _setupSignals(self):

		self._section_top.sig_frame_scale_changed.connect(self._viewmode_frame.setZoom)
		self._section_top.sig_script_scale_changed.connect(self._viewmode_script.setFrameScale)

		# NOTE: Maybe do this different?
		self._bin_view_model.sig_bin_view_info_set.connect(lambda: self.setTextColumnWidthsFromBin())

	def setShowColumnEditorAction(self, action:QtGui.QAction):
		"""Show column editor needs a global action"""

		self._viewmode_text.setShowColumnEditorAction(action)
		self._viewmode_script.setShowColumnEditorAction(action)

	###
	# View Mode Widgets
	###

	def textView(self) -> textview.BSBinTextView:
		"""Text View Mode widget"""

		return self._viewmode_text
	
	def frameView(self) -> frameview.BSBinFrameView:
		"""Frame View Mode widget"""

		return self._viewmode_frame

	def scriptView(self) -> scriptview.BSBinScriptViewDEPRECATEDBAD:
		"""Script View Mode widget"""
		
		return self._viewmode_script
	
	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current bin view mode"""

		logging.getLogger(__name__).debug("Setting bin view mode to %s", str(view_mode))
		
		old_view_mode = avbutils.bins.BinDisplayModes(self._section_main.currentIndex())
		
		if old_view_mode == view_mode:
			return

		self._section_main.setCurrentIndex(view_mode)
		self._section_top .setViewMode(view_mode)

		# Entering Frame View Mode
		# Sync selected items from selection model
		if view_mode == avbutils.bins.BinDisplayModes.FRAME:
			
			self._viewmode_frame.scene().setSelectedItems(
				list(x.row() for x in self._selection_model.selectedRows())
			)

		# Entering Script View Mode
		# Sync headers over to Script
#		elif view_mode == avbutils.bins.BinDisplayModes.SCRIPT:
#			pass

#			self._viewmode_script.syncFromHeader(self._viewmode_text.header())
			#self._viewmode_script.adjustFirstItemPadding()

		# Leaving Frame Mode
		# Sync selection back to selection model
		elif old_view_mode == avbutils.bins.BinDisplayModes.FRAME:

			self._selection_model.clearSelection()

			for row, item in enumerate(self._viewmode_frame.scene()._bin_items):

				if not item.isSelected():
					continue

				self._selection_model.select(
					self._bin_model_final.index(row, 0, QtCore.QModelIndex()),
					QtCore.QItemSelectionModel.SelectionFlag.Select | \
					  QtCore.QItemSelectionModel.SelectionFlag.Rows
				)

		self.sig_view_mode_changed.emit(view_mode)

	def viewMode(self) -> avbutils.BinDisplayModes:
		"""Current view mode"""

		return avbutils.BinDisplayModes(self._section_main.currentIndex())
	

	###
	# Bin Views and Filters
	###

	@QtCore.Slot(avbutils.bins.BinDisplayItemTypes)
	def setBinDisplayItemTypes(self, item_types:avbutils.bins.BinDisplayItemTypes):
		
		self._bin_items_filter.setAcceptedItemTypes(item_types)

	@QtCore.Slot(bool)
	def setBinColumnFiltersDisabled(self, are_disabled:bool):

		self.setBinColumnFiltersEnabled(not are_disabled)

	@QtCore.Slot(bool)
	def setBinColumnFiltersEnabled(self, are_enabled:bool):

		self._bin_view_filter.setEnabled(are_enabled)

		self.sig_bin_view_enabled.emit(are_enabled)

	@QtCore.Slot(bool)
	def setBinItemFiltersEnabled(self, are_enabled:bool):

		print("TO DO")
		self._bin_items_filter.setEnabled(are_enabled)

	@QtCore.Slot(int)
	def hideBinColumn(self, logical_index:int):

		self._bin_model_final.setHeaderData(logical_index, QtCore.Qt.Orientation.Horizontal, True, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

	@QtCore.Slot()
	@QtCore.Slot(str)
	def setSearchText(self, search_text:str):

		self._bin_find_filter.setSearchText(search_text)



	@QtCore.Slot(dict)
	def setTextColumnWidthsFromBin(self, column_widths:dict[str,int]|None=None):
		"""Set text view column widths from avid bin `dict[column_name:str, width:int]` or autosize if not there"""

		if column_widths and self._use_bin_column_widths:

			logging.getLogger(__name__).debug("Setting column widths from: %s", column_widths)

			for idx_logical in range(self.textView().header().count()):

				column_name = self.textView().model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

				if column_name in column_widths:

					logging.getLogger(__name__).debug("Setting column %s (%s) to width %s", column_name, idx_logical, column_widths[column_name])
					self.textView().setColumnWidth(idx_logical, column_widths[column_name])
					
				
				else:

					self.textView().resizeColumnToContents(idx_logical)
					logging.getLogger(__name__).debug("Set column %s (%s) to auto-fit width %s", column_name, idx_logical, self.textView().header().sectionSize(idx_logical))


		else:
			# Resize all columns to contents
			logging.getLogger(__name__).debug("Auto-sizing all columns")
			self.textView().header().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

	@QtCore.Slot(bool)
	def setSiftEnabled(self, is_enabled:bool):

		self._bin_sift_filter.setEnabled(is_enabled)

	@QtCore.Slot(object)
	def setSiftOptions(self, sift_options:typing.Iterable[avbutils.bins.BinSiftOption]):

		print("TODO")
		self._bin_sift_filter.setSiftOptions(sift_options)


	###
	# Bin Appearance
	###

	def useSavedBinColumnWidths(self) -> bool:
		"""Initially load saved bin column widths or nah"""

		return self._use_bin_column_widths
	
	@QtCore.Slot(bool)
	def setUseSavedBinColumnWidths(self, use_saved_widths:bool):
		"""Initially load saved bin column widths or nah.  False will auto-fit columns."""

		if self._use_bin_column_widths == use_saved_widths:
			return
		
		self._use_bin_column_widths = use_saved_widths

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
		
		self._viewmode_text   .setFont(bin_font)
		self._viewmode_frame  .setFont(bin_font)
		self._viewmode_script .setFont(bin_font)
		
		self.sig_bin_font_changed.emit(bin_font)

	###
	# Misc
	###

	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		"""Set text item padding"""

		self._viewmode_text  .setItemPadding(padding)
		self._viewmode_script.setItemPadding(padding)

	@QtCore.Slot(object)
	def focusBinColumn(self, column_info:binviewitemtypes.BSBinViewColumnInfo) -> bool:

		for col in range(self._bin_model_final.columnCount(QtCore.QModelIndex())):

			if self._bin_model_final.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.RawColumnInfo) == column_info:

				self._section_main.currentWidget().setFocus()
				self._viewmode_text.selectSection(col)

				# Get the index of the top visible row
				vertical_offset = self._viewmode_text.verticalScrollBar().value()

				self._viewmode_text.scrollTo(
					self._bin_model_final.index(0, col, QtCore.QModelIndex()),
					QtWidgets.QTreeView.ScrollHint.PositionAtCenter
				)

				self._viewmode_text.verticalScrollBar().setValue(vertical_offset)

				self.sig_focus_set_on_column.emit(col)

				return
		
		QtWidgets.QApplication.beep()

		return False

	###
	# Scrollbar widgets
	###

	def addScrollBarWidget(self, widget:QtWidgets.QWidget, view_mode:avbutils.bins.BinDisplayModes):

		widget.setFixedWidth(self._proxystyle_hscroll.pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent))
		self._section_main.widget(view_mode).scrollArea().addScrollBarWidget(widget, QtCore.Qt.AlignmentFlag.AlignLeft)

	
	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setBottomScrollbarScaleFactor(self, scale_factor:int|float):

		self._proxystyle_hscroll.setScrollbarScaleFactor(scale_factor)

		# .update()/.polish() doesn't work. Need to re-set each time?
		self._viewmode_text  .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)
	
	def scrollbarScaler(self) -> proxystyles.BSScrollBarStyle:
		"""The scaler for the horizontal scroll bar"""

		return self._proxystyle_hscroll
	
	def topWidgetBar(self) -> widgetbars.BSBinContentsTopWidgetBar:
		return self._section_top