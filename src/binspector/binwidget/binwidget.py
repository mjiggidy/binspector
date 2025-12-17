"""
The big fella
"""


import logging
import avb, avbutils

from PySide6 import QtCore, QtGui, QtWidgets

from . import proxystyles, scrollwidgets, widgetbars

from ..listview import treeview
from ..frameview import frameview
from ..scriptview import scriptview

from ..models import viewmodels
from ..widgets import buttons
from ..utils import palettes

DEFAULT_FRAME_ZOOM_RANGE  = avbutils.bins.THUMB_FRAME_MODE_RANGE
DEFAULT_FRAME_ZOOM_START  = DEFAULT_FRAME_ZOOM_RANGE.start

DEFAULT_SCRIPT_ZOOM_RANGE = avbutils.bins.THUMB_SCRIPT_MODE_RANGE
DEFAULT_SCRIPT_ZOOM_START = avbutils.bins.THUMB_SCRIPT_MODE_RANGE.start

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_view_mode_changed   = QtCore.Signal(object)
	sig_bin_palette_changed = QtCore.Signal(QtGui.QPalette)
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
		
		self._scene_frame       = QtWidgets.QGraphicsScene()

		# Save initial palette for later togglin'
		self._default_palette   = self.palette()
		self._bin_palette       = self.palette()
		self._default_font      = self.font()
		self._bin_font          = self.font()
		self._use_bin_appearance= True

		self._section_top       = widgetbars.BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		
		self._binitems_list     = treeview.BSBinTreeView()
		self._binitems_frame    = frameview.BSBinFrameView()
		self._binitems_script   = scriptview.BSBinScriptView()

		self._binstats_list     = scrollwidgets.BSBinStatsLabel()
		self._binstats_frame    = scrollwidgets.BSBinStatsLabel()

		self._setupWidgets()
		self._setupSignals()
		self._setupActions()
		
		self._setupBinModel()

	def _setupWidgets(self):

		# Top Tool Bar
		self._section_top._sld_frame_scale .setRange(DEFAULT_FRAME_ZOOM_RANGE.start, DEFAULT_FRAME_ZOOM_RANGE.stop)
		self._section_top._sld_script_scale.setRange(DEFAULT_SCRIPT_ZOOM_RANGE.start, DEFAULT_SCRIPT_ZOOM_RANGE.stop)

		self.layout().addWidget(self._section_top)

		# Main List, Frame, and Script views
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._binitems_list)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._binitems_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._binitems_script)

		self._binitems_frame.setZoomRange(DEFAULT_FRAME_ZOOM_RANGE)
		self._binitems_frame.setZoom(DEFAULT_FRAME_ZOOM_START)
		
		self.layout().addWidget(self._section_main)

		self._binitems_list.setModel(self._bin_filter_model)
		self._binitems_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		
		# NOTE: Set AFTER `view.setModel()`.  Got me good.
		self._binitems_list.setSelectionModel(self._selection_model)
		self._binitems_frame.scene().setSelectionModel(self._selection_model)
		

		# Adjust scrollbar height for macOS rounded corner junk

		# NOTE: `base_style` junk copies a new instance of the hbar base style, otherwise it goes out of scope
		# and segfaults on exit, which I really love.  I really love all of this.  I don't need money or a career.
		self._proxystyle_hscroll = proxystyles.BSScrollBarStyle(
			QtWidgets.QStyleFactory.create(QtWidgets.QApplication.style().name()),
			scale_factor=1,
			parent=self
		)

		self._binitems_list .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_frame.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

		self._binitems_list .addScrollBarWidget(self._binstats_list,  QtCore.Qt.AlignmentFlag.AlignLeft)
		self._binitems_frame.addScrollBarWidget(self._binstats_frame, QtCore.Qt.AlignmentFlag.AlignLeft)

		btn = buttons.BSActionPushButton(self._binitems_frame.actions().act_toggle_grid, show_text=False)
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedWidth(proxystyles.BSScrollBarStyle().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent))
		self._binitems_frame.addScrollBarWidget(
			btn,
			QtCore.Qt.AlignmentFlag.AlignLeft
		)

		btn = buttons.BSActionPushButton(self._binitems_frame.actions().act_toggle_map, show_text=False)
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedWidth(proxystyles.BSScrollBarStyle().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent))

		self._binitems_frame.addScrollBarWidget(
			btn,
			QtCore.Qt.AlignmentFlag.AlignLeft
		)

		btn = buttons.BSActionPushButton(self._binitems_frame.actions().act_toggle_ruler, show_text=False)
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedWidth(proxystyles.BSScrollBarStyle().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent))
		self._binitems_frame.addScrollBarWidget(
			btn,
			QtCore.Qt.AlignmentFlag.AlignLeft
		)

	def _setupSignals(self):
		
		self._bin_filter_model.rowsInserted  .connect(self.updateBinStats)
		self._bin_filter_model.rowsRemoved   .connect(self.updateBinStats)
		self._bin_filter_model.modelReset    .connect(self.updateBinStats)
		self._bin_filter_model.layoutChanged .connect(self.updateBinStats)

		self._section_top.sig_frame_scale_changed  .connect(self._binitems_frame.setZoom)
		self._binitems_frame.sig_zoom_level_changed.connect(self._section_top._sld_frame_scale.setValue)
		self._binitems_frame.sig_zoom_range_changed.connect(lambda r: self._section_top._sld_frame_scale.setRange(r.start, r.stop))

		self.sig_bin_stats_updated.connect(self._binstats_list.setText)
		self.sig_bin_stats_updated.connect(self._binstats_frame.setText)
		#self._binitems_frame.scene().sig_bin_item_selection_changed.connect(self.setSelectedItems)

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

	def listView(self) -> treeview.BSBinTreeView:
		"""Get the main view"""

		return self._binitems_list
	
#	def setListView(self, treeview:bintreeview.BSBinTreeView):
#
#		self._binitems_list = treeview
#		self._setViewModeWidget(avbutils.BinDisplayModes.LIST, self._binitems_list)

	def frameView(self) -> frameview.BSBinFrameView:
		return self._binitems_frame
	
#	def setFrameView(self, frame_view:binframeview.BSBinFrameView):
#
#		self._binitems_frame = frame_view
#		self._setViewModeWidget(avbutils.BinDisplayModes.FRAME, self._binitems_frame)

	def scriptView(self) -> scriptview.BSBinScriptView:
		return self._binitems_script
	
#	def setScriptView(self, script_view:binscriptview.BSBinScriptView):
#
#		self._binitems_script = script_view
#		self._setViewModeWidget(avbutils.BinDisplayModes.SCRIPT, self._binitems_script)

	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMargins):

		self._binitems_list.setItemPadding(padding)
	
	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setBottomScrollbarScaleFactor(self, scale_factor:int|float):

		self._proxystyle_hscroll.setScrollbarScaleFactor(scale_factor)

		# .update()/.polish() doesn't work. Need to re-set each time?
		self._binitems_list .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_frame.horizontalScrollBar().setStyle(self._proxystyle_hscroll)
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette) -> None:
		
		super().setPalette(palette)
		self.sig_bin_palette_changed.emit(palette)
		
		# TODO: Re-wire with styleWatcher
		# self._binitems_list._palette_watcher.setPalette(palette)
	
	def topWidgetBar(self) -> widgetbars.BSBinContentsTopWidgetBar:
		return self._section_top
	
	def setTopWidgetBar(self, toolbar:widgetbars.BSBinContentsTopWidgetBar):
		self._section_top = toolbar
	
	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		# TODO: Do I need to emit a confirmation signal here?
		self._bin_filter_model.setBinViewEnabled(is_enabled)

	@QtCore.Slot(object)
	def setBinAppearanceEnabled(self, is_enabled:bool):
		
		self._use_bin_appearance = is_enabled
		self.setPalette(self._bin_palette if is_enabled else self._default_palette)
		self.setFont(self._bin_font if is_enabled else self._default_font)

	@QtCore.Slot(object)
	def setUseSystemAppearance(self, use_system:bool):

		self.setBinAppearanceEnabled(not use_system)

	@QtCore.Slot(object)
	def setBinFiltersEnabled(self, is_enabled:bool):

		self._bin_filter_model.setBinFiltersEnabled(is_enabled)

	@QtCore.Slot(object)
	def setDisplayMode(self, mode:avbutils.BinDisplayModes):
		pass

	@QtCore.Slot(QtGui.QColor, QtGui.QColor)
	def setBinColors(self, fg_color:QtGui.QColor, bg_color:QtGui.QColor):

		palette = palettes.prep_palette(self.palette(), fg_color, bg_color)

		self._bin_palette = palette

		if self._use_bin_appearance:
			self.setPalette(self._bin_palette)
			
		
		#else:
		#	self.setPalette(self._default_palette)
	
	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, bin_font:QtGui.QFont):
		
		self._bin_font = bin_font
		
		if self._use_bin_appearance:
			self._binitems_list.setFont(bin_font)
			self._binitems_frame.setFont(bin_font)

	@QtCore.Slot()
	def updateBinStats(self):

		count_visible = self._bin_filter_model.rowCount()
		count_all     = self._bin_filter_model.sourceModel().rowCount()

		info_text = self.tr("Showing {current_item_count} of {total_item_count} items").format(
			current_item_count=QtCore.QLocale.system().toString(count_visible),
			total_item_count=QtCore.QLocale.system().toString(count_all)
		)
		
		self.sig_bin_stats_updated.emit(info_text)

	@QtCore.Slot(object, object, object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict[str,int], frame_scale:int):

		self.setBinViewName(bin_view.name)
		self.frameView().setZoom(frame_scale)
		self.frameView().ensureVisible(0, 0, 50, 50, 4,2)

	
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
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current view mode"""

		#print("SETTING VIEW MODE TO ", view_mode)

		self._section_main.setCurrentIndex(int(view_mode))
		self._section_top.setViewMode(view_mode)
		self.sig_view_mode_changed.emit(view_mode)

	def viewMode(self) -> avbutils.BinDisplayModes:
		"""Current view mode"""

		return avbutils.BinDisplayModes(self._section_main.currentIndex())
	
	@QtCore.Slot(bool)
	def setSiftEnabled(self, is_enabled:bool):

		self._bin_filter_model.setSiftEnabled(is_enabled)

	@QtCore.Slot(object)
	def setSiftOptions(self, sift_options:avbutils.bins.BinSiftOption):

		self._bin_filter_model.setSiftOptions(sift_options)

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

	def addScrollBarWidget(self, widget:QtWidgets.QWidget, alignment:QtCore.Qt.AlignmentFlag):

		widget.setFixedWidth(
			self._proxystyle_hscroll.pixelMetric(
				QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent
			)
		)
		
		self._binitems_list.addScrollBarWidget(widget, alignment)