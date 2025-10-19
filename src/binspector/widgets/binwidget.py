from PySide6 import QtCore, QtGui, QtWidgets
import avbutils
from ..views import bintreeview, binframeview, binscriptview
from . import buttons

class BSBinContentsWidgetBar(QtWidgets.QWidget):
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

class BSBinContentsBottomWidgetBar(BSBinContentsWidgetBar):
	"""Default bottom widget bar"""

	def __init__(self, *args, **kwargs):


		super().__init__(*args, **kwargs)
		
		if not isinstance(self, QtWidgets.QToolBar):
			self.setLayout(QtWidgets.QGridLayout())
			self.layout().setContentsMargins(*[4]*4)
		
		self._txt_info = QtWidgets.QLabel()
		self._txt_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

		self.layout().addWidget(self._txt_info)
		
		
	@QtCore.Slot(object)
	def setInfoText(self, text:str):

		self._txt_info.setText(text)
		
class BSBinContentsTopWidgetBar(BSBinContentsWidgetBar):
	"""Default top widget bar"""

	sig_search_text_changed = QtCore.Signal(object)
	"""Search text has changed"""

	sig_binview_selected = QtCore.Signal(object)
	"""User changed the binview"""
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		if not isinstance(self, QtWidgets.QToolBar):
			self.setLayout(QtWidgets.QHBoxLayout())
			self.layout().setContentsMargins(*[4]*4)

		self._btngrp_file         = QtWidgets.QButtonGroup()
		self._btn_open            = buttons.LBPushButtonAction()
		self._btn_reload          = buttons.LBPushButtonAction(show_text=False)
		self._btn_stop            = buttons.LBPushButtonAction(show_text=False)

		self._prg_loading         = QtWidgets.QProgressBar()

		self._btngrp_viewmode     = QtWidgets.QButtonGroup()
		self._btn_viewmode_list   = buttons.LBPushButtonAction(show_text=False)
		self._btn_viewmode_frame  = buttons.LBPushButtonAction(show_text=False)
		self._btn_viewmode_script = buttons.LBPushButtonAction(show_text=False)

		self._cmb_binviews    = QtWidgets.QComboBox()
		self._txt_search      = QtWidgets.QLineEdit()

		self._setupWidgets()

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
		self.addWidget(self._cmb_binviews)

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

		self._txt_search.textEdited.connect(self.sig_search_text_changed)
	
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

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_view_mode_changed = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())

		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)

		self._section_top       = BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		self._section_bottom    = BSBinContentsBottomWidgetBar()
		
		self._binitems_list     = bintreeview.BSBinTreeView()
		self._binitems_frame    = binframeview.BSBinFrameView()
		self._binitems_script   = binscriptview.BSBinScriptView()

		self.layout().addWidget(self._section_top)
		self.layout().addWidget(self._section_main)
		self.layout().addWidget(self._section_bottom)

		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._binitems_list)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._binitems_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._binitems_script)

		self._binitems_list.model().rowsInserted .connect(self.updateBinStats)
		self._binitems_list.model().rowsRemoved  .connect(self.updateBinStats)
		self._binitems_list.model().modelReset   .connect(self.updateBinStats)

		self._section_bottom.setLayout(QtWidgets.QHBoxLayout())
		self._section_bottom.layout().setContentsMargins(2,2,2,2)

	def _setViewModeWidget(self, mode:avbutils.BinDisplayModes, widget:QtWidgets.QWidget):
		"""Set view mode widget delegate for the stacked widget"""

		self._section_main.removeWidget(self._section_main.widget(int(mode)))
		self._section_main.insertWidget(int(mode), widget)

	def listView(self) -> bintreeview.BSBinTreeView:
		"""Get the main view"""

		return self._binitems_list
	
	def setListView(self, treeview:bintreeview.BSBinTreeView):

		self._binitems_list = treeview
		self._setViewModeWidget(avbutils.BinDisplayModes.LIST, self._binitems_list)

	def frameView(self) -> binframeview.BSBinFrameView:
		return self._binitems_frame
	
	def setFrameView(self, frame_view:binframeview.BSBinFrameView):

		self._binitems_frame = frame_view
		self._setViewModeWidget(avbutils.BinDisplayModes.FRAME, self._binitems_frame)

	def scriptView(self) -> binscriptview.BSBinScriptView:
		return self._binitems_script
	
	def setScriptView(self, script_view:binscriptview.BSBinScriptView):

		self._binitems_script = script_view
		self._setViewModeWidget(avbutils.BinDisplayModes.SCRIPT, self._binitems_script)
	
	def topWidgetBar(self) -> BSBinContentsTopWidgetBar:
		return self._section_top
	
	def setTopWidgetBar(self, toolbar:BSBinContentsTopWidgetBar):
		self._section_top = toolbar
	
	def bottomWidgetBar(self) -> BSBinContentsBottomWidgetBar:
		return self._section_bottom
	
	def setBottomWidgetBar(self, widget:BSBinContentsBottomWidgetBar):
		self._section_bottom = widget
	
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
		palette.setColor(QtGui.QPalette.ColorRole.Light,    palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION))      # Lighter than Button color
		palette.setColor(QtGui.QPalette.ColorRole.Midlight, palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION_MID))  # Between Button and Light
		palette.setColor(QtGui.QPalette.ColorRole.Mid,      palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION_MID))   # Between Button and Dark
		palette.setColor(QtGui.QPalette.ColorRole.Dark,     palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION))       # Darker than Button

		self.setPalette(palette)
	
	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, bin_font:QtGui.QFont):
		self._binitems_list.setFont(bin_font)

	@QtCore.Slot()
	def updateBinStats(self):

		count_visible = self._binitems_list.model().rowCount()
		count_all     = self._binitems_list.model().sourceModel().rowCount()
		self._section_bottom.setInfoText(
			f"Showing {QtCore.QLocale.system().toString(count_visible)} of {QtCore.QLocale.system().toString(count_all)} items"
		)
	
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

		print("SETTING VIEW MODE TO ", view_mode)

		self._section_main.setCurrentIndex(int(view_mode))
		self.sig_view_mode_changed.emit(view_mode)

	def viewMode(self) -> avbutils.BinDisplayModes:
		"""Current view mode"""

		return avbutils.BinDisplayModes(self._section_main.currentIndex())