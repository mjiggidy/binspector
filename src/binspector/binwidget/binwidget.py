"""
The big fella
"""

import logging
import avb, avbutils

from PySide6 import QtCore, QtGui, QtWidgets

from . import proxystyles, scrollwidgets, widgetbars

from ..textview import textview
from ..frameview import frameview
from ..scriptview import scriptview

from ..models import viewmodels

from ..core.config import BSFrameViewModeConfig, BSScriptViewModeConfig

BIN_ITEM_TYPE_ICON_REGISTRY:textview.IconRegistryType = {

	avbutils.bins.BinDisplayItemTypes.MASTER_CLIP|avbutils.bins.BinDisplayItemTypes.USER_CLIP:      ":/icons/binitems/item_masterclip.svg",
	avbutils.bins.BinDisplayItemTypes.MASTER_CLIP|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP: ":/icons/binitems/item_masterclip.svg",
	avbutils.bins.BinDisplayItemTypes.LINKED_MASTER_CLIP|avbutils.bins.BinDisplayItemTypes.USER_CLIP:      ":/icons/binitems/item_linkedclip.svg",
	avbutils.bins.BinDisplayItemTypes.LINKED_MASTER_CLIP|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP: ":/icons/binitems/item_linkedclip.svg",
	avbutils.bins.BinDisplayItemTypes.STEREOSCOPIC_CLIP|avbutils.bins.BinDisplayItemTypes.USER_CLIP: ":/icons/binitems/item_stereoclip.svg",
	avbutils.bins.BinDisplayItemTypes.STEREOSCOPIC_CLIP|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP: ":/icons/binitems/item_stereoclip.svg",
	avbutils.bins.BinDisplayItemTypes.SUBCLIP|avbutils.bins.BinDisplayItemTypes.USER_CLIP:          ":/icons/binitems/item_subclip.svg",
	avbutils.bins.BinDisplayItemTypes.SUBCLIP|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP:     ":/icons/binitems/item_subclip.svg",
	avbutils.bins.BinDisplayItemTypes.SEQUENCE|avbutils.bins.BinDisplayItemTypes.USER_CLIP:         ":/icons/binitems/item_timeline.svg",
	avbutils.bins.BinDisplayItemTypes.SEQUENCE|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP:    ":/icons/binitems/item_timeline.svg",
	avbutils.bins.BinDisplayItemTypes.GROUP|avbutils.bins.BinDisplayItemTypes.USER_CLIP:            ":/icons/binitems/item_groupclip.svg",
	avbutils.bins.BinDisplayItemTypes.GROUP|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP:       ":/icons/binitems/item_groupclip.svg",
	avbutils.bins.BinDisplayItemTypes.SOURCE|avbutils.bins.BinDisplayItemTypes.USER_CLIP:            ":/icons/binitems/item_source.svg",
	avbutils.bins.BinDisplayItemTypes.SOURCE|avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP:       ":/icons/binitems/item_source.svg",
}


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

		# Save initial palette for later togglin'
		self._default_palette   = self.palette()
		self._bin_palette       = self.palette()
		self._default_font      = self.font()
		self._bin_font          = self.font()
		self._use_bin_appearance= True

		self._section_top       = widgetbars.BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		
		self._viewmode_text     = textview.BSBinTextView()
		self._viewmode_frame    = frameview.BSBinFrameView()
		self._viewmode_script   = scriptview.BSBinScriptView()

		self._binstats_text     = scrollwidgets.BSBinStatsLabel()
		self._binstats_frame    = scrollwidgets.BSBinStatsLabel()

		# Create proxy style from application style for potential horizontal scrollbar height mods
		self._proxystyle_hscroll = proxystyles.BSScrollBarStyle(parent=self)

		self._setupWidgets()
		self._setupSignals()
		self._setupActions()
		
		self._setupBinModel()

	def _setupWidgets(self):

		# Top Tool Bar
		self._section_top._sld_frame_scale .setRange(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE.start,   BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE.stop)
		self._section_top._sld_script_scale.setRange(BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_RANGE.start, BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_RANGE.stop)

		self.layout().addWidget(self._section_top)

		# Main Text, Frame, and Script views
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._viewmode_text)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._viewmode_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._viewmode_script)

		self._viewmode_frame.setZoomRange(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE)
		self._viewmode_frame.setZoom(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_START)
		
		self.layout().addWidget(self._section_main)

		
		self._viewmode_text.setModel(self._bin_filter_model)
		self._viewmode_text.setBinItemIconRegistry(BIN_ITEM_TYPE_ICON_REGISTRY)
		self._viewmode_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

		self._viewmode_script.setModel(self._bin_filter_model)
		self._viewmode_script.setBinItemIconRegistry(BIN_ITEM_TYPE_ICON_REGISTRY)
		self._viewmode_script.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		
		# NOTE: Set AFTER `view.setModel()`.  Got me good.
		self._viewmode_text.setSelectionModel(self._selection_model)
		self._viewmode_script.setSelectionModel(self._selection_model)
		
		# Adjust scrollbar height for macOS rounded corner junk
		self._viewmode_text  .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

		self._viewmode_text .addScrollBarWidget(self._binstats_text,  QtCore.Qt.AlignmentFlag.AlignLeft)
		self._viewmode_frame.addScrollBarWidget(self._binstats_frame, QtCore.Qt.AlignmentFlag.AlignLeft)

	def _setupSignals(self):
		
		self._bin_filter_model.rowsInserted  .connect(self.updateBinStats)
		self._bin_filter_model.rowsRemoved   .connect(self.updateBinStats)
		self._bin_filter_model.modelReset    .connect(self.updateBinStats)
		self._bin_filter_model.layoutChanged .connect(self.updateBinStats)

		self._section_top.sig_frame_scale_changed  .connect(self._viewmode_frame.setZoom)
		self._viewmode_frame.sig_zoom_level_changed.connect(self._section_top._sld_frame_scale.setValue)
		self._viewmode_frame.sig_zoom_range_changed.connect(lambda r: self._section_top._sld_frame_scale.setRange(r.start, r.stop))

		self._section_top.sig_script_scale_changed         .connect(self._viewmode_script.setFrameScale)
		self._viewmode_script.sig_frame_scale_changed      .connect(self._section_top._sld_script_scale.setValue)
		self._viewmode_script.sig_frame_scale_range_changed.connect(lambda r: self._section_top._sld_script_scale.setRange(r.start, r.stop))

		self.sig_bin_stats_updated.connect(self._binstats_text.setText)
		self.sig_bin_stats_updated.connect(self._binstats_frame.setText)


		
		#self._binitems_frame.scene().sig_bin_item_selection_changed.connect(self.setSelectedItems)

		#self._section_main.currentChanged.connect(self._selection_syncer.viewModeChanged)
		#self._selection_syncer.sig_frame_selection_changed.connect(print)

	def _setupActions(self):

		self._act_set_view_width_for_columns = QtGui.QAction(self._viewmode_text)
		self._act_set_view_width_for_columns.setText(self.tr("Restore saved bin column widths"))
		self._act_set_view_width_for_columns.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_T))
		self._act_set_view_width_for_columns.triggered.connect(lambda: self._viewmode_text.setColumnWidthsFromBinView(QtCore.QModelIndex(), 0, self._viewmode_text.header().count()-1))

		self._act_autofit_columns = QtGui.QAction(self._viewmode_text)
		self._act_autofit_columns.setText(self.tr("Auto-fit bin columns to contents"))
		self._act_autofit_columns.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.Key.Key_T))
		self._act_autofit_columns.triggered.connect(self._viewmode_text.resizeAllColumnsToContents)
		
		self._viewmode_text.addAction(self._act_set_view_width_for_columns)
		self._viewmode_text.addAction(self._act_autofit_columns)
			


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
		self._viewmode_frame.scene().setBinFilterModel(self._bin_filter_model) # TODO: Don't need to set each time? CHECK

	###
	# View Mode Widgets
	###

	def textView(self) -> textview.BSBinTextView:
		"""Text View Mode widget"""

		return self._viewmode_text
	
	def frameView(self) -> frameview.BSBinFrameView:
		"""Frame View Mode widget"""

		return self._viewmode_frame

	def scriptView(self) -> scriptview.BSBinScriptView:
		"""Script View Mode widget"""
		
		return self._viewmode_script
	
	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current bin view mode"""

		#logging.getLogger(__name__).debug("Setting bin view mode to %s", str(view_mode))
		
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
		elif view_mode == avbutils.bins.BinDisplayModes.SCRIPT:

			self._viewmode_script.syncFromHeader(self._viewmode_text.header())
			#self._viewmode_script.adjustFirstItemPadding()

		# Leaving Frame Mode
		# Sync selection back to selection model
		elif old_view_mode == avbutils.bins.BinDisplayModes.FRAME:

			self._selection_model.clearSelection()

			for row, item in enumerate(self._viewmode_frame.scene()._bin_items):

				if not item.isSelected():
					continue

				self._selection_model.select(
					self._bin_filter_model.index(row, 0, QtCore.QModelIndex()),
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

	@QtCore.Slot(object, object, int, int)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict[str,int], frame_scale:int, script_scale:int):

		self.setBinViewName(bin_view.name)

		for col in range(self.textView().header().count()):
			self.textView().setColumnWidthFromBinView(col, True)
			
		self.frameView().setZoom(frame_scale)
		self.frameView().ensureVisible(0, 0, 50, 50, 4,2)
		
		self.scriptView().setFrameScale(script_scale)


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

	@QtCore.Slot(str)
	def focusBinColumn(self, focus_field_name:str) -> bool:

		for log_idx, field_name in enumerate(
			[self._viewmode_text.model().headerData(i, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+5)
			for i in range(self._viewmode_text.header().count())]
			):

			if field_name == focus_field_name:

				self._section_main.currentWidget().setFocus()
				self._viewmode_text.selectSection(log_idx)
				self._viewmode_text.scrollTo(
					self._viewmode_text.model().index(0, log_idx, QtCore.QModelIndex()),
					QtWidgets.QTreeView.ScrollHint.PositionAtCenter
				)
				
				self.sig_focus_set_on_column.emit(log_idx)
				return True
		
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

	@QtCore.Slot()
	def updateBinStats(self):

		count_visible = self._bin_filter_model.rowCount()
		count_all     = self._bin_filter_model.sourceModel().rowCount()

		info_text = self.tr("Showing {current_item_count} of {total_item_count} items").format(
			current_item_count=QtCore.QLocale.system().toString(count_visible),
			total_item_count=QtCore.QLocale.system().toString(count_all)
		)
		
		self.sig_bin_stats_updated.emit(info_text)