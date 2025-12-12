import logging
from PySide6 import QtCore, QtGui, QtWidgets
import avbutils, avb
from ..views import bintreeview, binframeview, binscriptview
from ..models import sceneitems, viewmodels
from . import buttons, sliders
from ..managers import binproperties

class BSAbstractBinContentsWidgetBar(QtWidgets.QWidget):
	"""Widget bar to display above/below"""

	# TODO: I don't know lol might want this later

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)
		
		self.setSizePolicy(
			self.sizePolicy().horizontalPolicy(),
			QtWidgets.QSizePolicy.Policy.Maximum
		)

	def addWidget(self, widget:QtWidgets.QWidget):
		"""
		Add a widget to the layout.
		Doing this while I decide if this is a QToolBar or not.
		"""
		
		if isinstance(self, QtWidgets.QToolBar):
			super().addWidget(widget)
		else:
			self.layout().addWidget(widget)
		
class BSBinContentsTopWidgetBar(BSAbstractBinContentsWidgetBar):
	"""Default top widget bar"""

	sig_search_text_changed = QtCore.Signal(object)
	"""Search text has changed"""

	sig_binview_selected = QtCore.Signal(object)
	"""User changed the binview"""

	sig_frame_scale_changed  = QtCore.Signal(int)
	"""User changed frame thumb scale slider"""

	sig_script_scale_changed = QtCore.Signal(int)
	"""User changed script thumb scale slider"""
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		if not isinstance(self, QtWidgets.QToolBar):
			self.setLayout(QtWidgets.QHBoxLayout())
			self.layout().setContentsMargins(*[4]*4)

		self._btngrp_file         = QtWidgets.QButtonGroup()
		self._btn_open            = buttons.BSPushButtonAction()
		self._btn_reload          = buttons.BSPushButtonAction(show_text=False)
		self._btn_stop            = buttons.BSPushButtonAction(show_text=False)

		self._prg_loading         = QtWidgets.QProgressBar()

		self._btngrp_viewmode     = QtWidgets.QButtonGroup()
		self._btn_viewmode_list   = buttons.BSPushButtonAction(show_text=False)
		self._btn_viewmode_frame  = buttons.BSPushButtonAction(show_text=False)
		self._btn_viewmode_script = buttons.BSPushButtonAction(show_text=False)

		self._mode_controls       = QtWidgets.QStackedWidget()
		self._cmb_binviews        = QtWidgets.QComboBox()
		self._sld_frame_scale     = sliders.ViewModeSlider()
		self._sld_script_scale    = sliders.ViewModeSlider()
		
		self._txt_search          = QtWidgets.QLineEdit()

		self._setupWidgets()
		self._setupSignals()

	def _setupWidgets(self):

		self._btngrp_file.addButton(self._btn_open)
		self._btngrp_file.addButton(self._btn_reload)
		self._btngrp_file.addButton(self._btn_stop)
		self.addWidget(buttons.BSPushButtonActionBar(self._btngrp_file))

		self.addWidget(self._prg_loading)

		self._cmb_binviews.setSizePolicy(self._cmb_binviews.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		self._cmb_binviews.setMinimumWidth(self._cmb_binviews.fontMetrics().averageCharWidth() * 24)
		self._cmb_binviews.setMaximumWidth(self._cmb_binviews.fontMetrics().averageCharWidth() * 32)
		self._cmb_binviews.addItem("")
		self._cmb_binviews.insertSeparator(1)

		#self._sld_frame_scale.setRange(
		#	avbutils.bins.THUMB_FRAME_MODE_RANGE.start,
		#	avbutils.bins.THUMB_FRAME_MODE_RANGE.stop,
		#)

		self._sld_script_scale.setRange(
			avbutils.bins.THUMB_SCRIPT_MODE_RANGE.start,
			avbutils.bins.THUMB_SCRIPT_MODE_RANGE.stop,
		)
		
		self._mode_controls.addWidget(self._cmb_binviews)
		self._mode_controls.addWidget(self._sld_frame_scale)
		self._mode_controls.addWidget(self._sld_script_scale)
		self._mode_controls.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		#self._mode_controls.setCurrentIndex(1)
		self.addWidget(self._mode_controls)

		self._btn_viewmode_list  .setIconSize(QtCore.QSize(16,16))
		self._btn_viewmode_frame .setIconSize(QtCore.QSize(16,16))
		self._btn_viewmode_script.setIconSize(QtCore.QSize(16,16))

		self._btngrp_viewmode.setExclusive(True)
		self._btngrp_viewmode.addButton(self._btn_viewmode_list)
		self._btngrp_viewmode.addButton(self._btn_viewmode_frame)
		self._btngrp_viewmode.addButton(self._btn_viewmode_script)
		self.addWidget(buttons.BSPushButtonActionBar(self._btngrp_viewmode))

		self._txt_search.setSizePolicy(self.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		self._txt_search.setMinimumWidth(self._txt_search.fontMetrics().averageCharWidth() * 24)
		self._txt_search.setMaximumWidth(self._txt_search.fontMetrics().averageCharWidth() * 32)
		self._txt_search.setPlaceholderText("Find in bin")
		self._txt_search.setClearButtonEnabled(True)
		self.addWidget(self._txt_search)

	def _setupSignals(self):

		self._sld_frame_scale.sliderMoved.connect(self.sig_frame_scale_changed)
		self._sld_frame_scale.valueChanged.connect(lambda s: self._sld_frame_scale.setToolTip(str(s)))
		#self._sld_frame_scale.valueChanged.connect(print)
		self._sld_script_scale.sliderMoved.connect(self.sig_script_scale_changed)

		#self._txt_search.textEdited.connect(self.sig_search_text_changed)
	
	def setOpenBinAction(self, action:QtGui.QAction):
		"""Set the action for Open Bin"""

		self._btn_open.setAction(action)

	def setReloadBinAction(self, action:QtGui.QAction):
		"""Set the action for Reload Bin"""

		self._btn_reload.setAction(action)

	def setStopLoadAction(self, action:QtGui.QAction):
		"""Set the action for Stop Load"""

		self._btn_stop.setAction(action)

	def setViewModeListAction(self, action:QtGui.QAction):
		"""Set the action for view mode: list"""

		self._btn_viewmode_list.setAction(action)
	
	def setViewModeFrameAction(self, action:QtGui.QAction):
		"""Set the action for iew mode: frame"""

		self._btn_viewmode_frame.setAction(action)

	def setViewModeScriptAction(self, action:QtGui.QAction):
		"""Set the action for iew mode: script"""

		self._btn_viewmode_script.setAction(action)

	def searchBox(self) -> QtWidgets.QLineEdit:
		"""Return the search box"""

		return self._txt_search
	
	def binViewSelector(self) -> QtWidgets.QComboBox:

		return self._cmb_binviews
	
	def progressBar(self) -> QtWidgets.QProgressBar:

		return self._prg_loading
	
	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):

		self._mode_controls.setCurrentIndex(int(view_mode))

class BSScrollBarStyle(QtWidgets.QProxyStyle):
	"""Modify scrollbar height"""

	def __init__(self, *args, scale_factor:int|float=1.25, **kwargs):

		super().__init__(*args, **kwargs)
		self._scale_factor = scale_factor
	
	def pixelMetric(self, metric:QtWidgets.QStyle.PixelMetric, option:QtWidgets.QStyleOption=None, widget:QtWidgets.QWidget=None):

		if metric == QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent:
			return round(self.baseStyle().pixelMetric(metric, option, widget) * self._scale_factor)
		else:
			return self.baseStyle().pixelMetric(metric, option, widget)
	
	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setScrollbarScaleFactor(self, scale_factor:float|int):
		#print("YOOO", scale_factor)
		self._scale_factor = scale_factor

class BSBinStatsLabel(QtWidgets.QLabel):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		f = self.font()
		f.setPointSizeF(f.pointSizeF() * 0.8)
		self.setFont(f)
		self.setMinimumWidth(self.fontMetrics().averageCharWidth() * 32)	# Showing 999,999 of 999,999 items
		self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel|QtWidgets.QFrame.Shadow.Sunken)
		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, self.sizePolicy().verticalPolicy())

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_view_mode_changed   = QtCore.Signal(object)
	sig_bin_palette_changed = QtCore.Signal(QtGui.QPalette)
	sig_bin_model_changed   = QtCore.Signal(object)
	sig_focus_set_on_column = QtCore.Signal(int)	# Logical column index
	sig_bin_stats_updated   = QtCore.Signal(str)

	def __init__(self, *args, bin_model:viewmodels.LBTimelineViewModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)
		
		self._bin_model         = bin_model or viewmodels.LBTimelineViewModel()
		self._bin_filter_model  = viewmodels.LBSortFilterProxyModel()
		self._selection_model   = QtCore.QItemSelectionModel(self._bin_filter_model, parent=self)
		
		self._scene_frame       = QtWidgets.QGraphicsScene()

		# Save initial palette for later togglin'
		self._default_palette   = self.palette()
		self._bin_palette       = self.palette()
		self._default_font      = self.font()
		self._bin_font          = self.font()
		self._use_bin_appearance= True

		self._section_top       = BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		
		self._binitems_list     = bintreeview.BSBinTreeView()
		self._binitems_frame    = binframeview.BSBinFrameView()
		self._binitems_script   = binscriptview.BSBinScriptView()

		self._binstats_list     = BSBinStatsLabel()
		self._binstats_frame    = BSBinStatsLabel()

		self._setupWidgets()
		self._setupSignals()
		self._setupActions()
		
		self._setupBinModel()

	def _setupWidgets(self):

		self.layout().addWidget(self._section_top)

		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._binitems_list)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._binitems_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._binitems_script)
		
		self.layout().addWidget(self._section_main)

		self._binitems_list.setModel(self._bin_filter_model)
		self._binitems_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		
		# NOTE: Set AFTER `view.setModel()`.  Got me good.
		self._binitems_list.setSelectionModel(self._selection_model)
		self._binitems_frame.scene().setSelectionModel(self._selection_model)
		

		# Adjust scrollbar height for macOS rounded corner junk
		# NOTE: `base_style` junk copies a new instance of the hbar base style, otherwise it goes out of scope
		# and segfaults on exit, which I really love.  I really love all of this.  I don't need money or a career.
		base_style = QtWidgets.QStyleFactory.create(self._binitems_list.horizontalScrollBar().style().objectName())
		self._proxystyle_hscroll = BSScrollBarStyle(base_style, scale_factor=1.25, parent=self)

		self._binitems_list .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._binitems_frame.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

		self._binitems_frame.setZoomRange(avbutils.bins.THUMB_FRAME_MODE_RANGE)
		self._binitems_frame.setZoom(self._section_top._sld_frame_scale.minimum())
		self._section_top._sld_frame_scale.setRange(self._binitems_frame.zoomRange().start, self._binitems_frame.zoomRange().stop)
		# TODO: Necessary?
		#logging.getLogger(__name__).error("Zoom range set to %s, confirm: %s", avbutils.bins.THUMB_FRAME_MODE_RANGE, self._binitems_frame.zoomRange())

		
		
		self._binitems_list .addScrollBarWidget(self._binstats_list,  QtCore.Qt.AlignmentFlag.AlignLeft)
		self._binitems_frame.addScrollBarWidget(self._binstats_frame, QtCore.Qt.AlignmentFlag.AlignLeft)
		

	def _setupSignals(self):
		
		self._bin_filter_model.rowsInserted  .connect(self.updateBinStats)
		self._bin_filter_model.rowsRemoved   .connect(self.updateBinStats)
		self._bin_filter_model.modelReset    .connect(self.updateBinStats)
		self._bin_filter_model.layoutChanged .connect(self.updateBinStats)

		self._section_top.sig_frame_scale_changed.connect(self._binitems_frame.setZoom)
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
	def setBinModel(self, bin_model:viewmodels.LBTimelineViewModel):
		"""Set the bin item model for the bin"""

		if self._bin_model == bin_model:
			return
		
		self._bin_model = bin_model
		self._setupBinModel()
		
		logging.getLogger(__name__).debug("Set bin model=%s", self._bin_model)
		self.sig_bin_model_changed.emit(bin_model)
	
	def binModel(self) -> viewmodels.LBTimelineViewModel:
		return self._bin_model
	
	def _setupBinModel(self):
		"""Connect bin model to all the schtuff"""

		self._bin_filter_model.setSourceModel(self._bin_model)
		self._binitems_frame.scene().setBinFilterModel(self._bin_filter_model) # TODO: Don't need to set each time? CHECK

	def listView(self) -> bintreeview.BSBinTreeView:
		"""Get the main view"""

		return self._binitems_list
	
#	def setListView(self, treeview:bintreeview.BSBinTreeView):
#
#		self._binitems_list = treeview
#		self._setViewModeWidget(avbutils.BinDisplayModes.LIST, self._binitems_list)

	def frameView(self) -> binframeview.BSBinFrameView:
		return self._binitems_frame
	
#	def setFrameView(self, frame_view:binframeview.BSBinFrameView):
#
#		self._binitems_frame = frame_view
#		self._setViewModeWidget(avbutils.BinDisplayModes.FRAME, self._binitems_frame)

	def scriptView(self) -> binscriptview.BSBinScriptView:
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
		self._binitems_list.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette) -> None:
		
		super().setPalette(palette)
		self.sig_bin_palette_changed.emit(palette)
		self._binitems_list._palette_watcher.setPalette(palette)
	
	def topWidgetBar(self) -> BSBinContentsTopWidgetBar:
		return self._section_top
	
	def setTopWidgetBar(self, toolbar:BSBinContentsTopWidgetBar):
		self._section_top = toolbar
	
#	def bottomWidgetBar(self) -> BSBinContentsBottomWidgetBar:
#		return self._section_bottom
#	
#	def setBottomWidgetBar(self, widget:BSBinContentsBottomWidgetBar):
#		self._section_bottom = widget
	
	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		# TODO: Do I need to emit a confirmation signal here?
		self._bin_filter_model.setBinViewEnabled(is_enabled)

	@QtCore.Slot(object)
	def setBinAppearanceEnabled(self, is_enabled:bool):
		
		self._use_bin_appearance = is_enabled
		self.setPalette(self._bin_palette if is_enabled else self._default_palette)
		self._binitems_list.setFont(self._bin_font if is_enabled else self._default_font)

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

		VARIATION     = 110  # Must be >100 to  have effect
		VARIATION_MID = 105  # Must be >100 to  have effect

		palette = self.palette()

		palette.setColor(QtGui.QPalette.ColorRole.Text,            fg_color)
		palette.setColor(QtGui.QPalette.ColorRole.ButtonText,      fg_color)
		palette.setColor(QtGui.QPalette.ColorRole.Base,            bg_color)
		palette.setColor(QtGui.QPalette.ColorRole.AlternateBase,   bg_color.darker(VARIATION))
		palette.setColor(QtGui.QPalette.ColorRole.Button,          bg_color.darker(VARIATION))

		palette.setColor(QtGui.QPalette.ColorRole.WindowText,      fg_color)
		palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, bg_color.lighter(VARIATION).lighter(VARIATION).lighter(VARIATION))
		palette.setColor(QtGui.QPalette.ColorRole.Window,          bg_color.darker(VARIATION).darker(VARIATION))


		# Fusion scrollbar uses these colors per https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html
		# Although it... like... doesn't? lol
		palette.setColor(QtGui.QPalette.ColorRole.Light,    palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION))      # Lighter than Button color
		palette.setColor(QtGui.QPalette.ColorRole.Midlight, palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION_MID))  # Between Button and Light
		palette.setColor(QtGui.QPalette.ColorRole.Mid,      palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION_MID))   # Between Button and Dark
		palette.setColor(QtGui.QPalette.ColorRole.Dark,     palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION))       # Darker than Button

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


		#self.frameView().translate(500, 500)
		#self.frameView().setSceneRect(QtCore.QRect(QtCore.QPoint(-2500, -2500), QtCore.QSize(5000, 5000)))
		#self.frameView().centerOn(0,0)
		#print("***********", self.frameView().sceneRect())
		#print("***********", self.frameView().viewport().rect())
		self.frameView().setZoom(frame_scale)
		self.frameView().ensureVisible(0, 0, 50, 50, 4,2)
		#self.frameView().centerOn(QtCore.QPointF(0,0))

	
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
		#self._binitems_frame.addScrollBarWidget(widget, alignment)