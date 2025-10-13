from PySide6 import QtCore, QtGui, QtWidgets
import avbutils
from ..views import bintreeview
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
		
		if not isinstance(self, QtWidgets.QToolBar):
			self.setLayout(QtWidgets.QHBoxLayout())
			self.layout().setContentsMargins(*[4]*4)

	def addWidget(self, widget:QtWidgets.QWidget):
		"""
		Add a widget to the layout.
		Doing this while I decide if this is a QToolBar or not.
		"""
		
		if isinstance(self, QtWidgets.QToolBar):
			super().addWidget(widget)
		else:
			self.layout().addWidget(widget)
		
class BSBinContentsTopWidgetBar(BSBinContentsWidgetBar):
	"""Default top widget bar"""

	sig_search_text_changed = QtCore.Signal(object)
	"""Search text has changed"""

	sig_binview_selected = QtCore.Signal(object)
	"""User changed the binview"""
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._btn_open            = buttons.LBPushButtonAction()

		self._btngrp_viewmode     = QtWidgets.QButtonGroup()
		self._btn_viewmode_list   = buttons.LBPushButtonAction(show_text=False)
		self._btn_viewmode_frame  = buttons.LBPushButtonAction(show_text=False)
		self._btn_viewmode_script = buttons.LBPushButtonAction(show_text=False)

		self._cmb_binviews    = QtWidgets.QComboBox()
		self._txt_search      = QtWidgets.QLineEdit()

		self._setupWidgets()

	def _setupWidgets(self):

		self.addWidget(self._btn_open)
		
		if isinstance(self, QtWidgets.QToolBar):
			self.addSeparator()
		else:
			self.layout().addStretch()
		
		self._btngrp_viewmode.setExclusive(True)
		self._btngrp_viewmode.addButton(self._btn_viewmode_list)
		self._btngrp_viewmode.addButton(self._btn_viewmode_frame)
		self._btngrp_viewmode.addButton(self._btn_viewmode_script)

		self._cmb_binviews.setSizePolicy(self._cmb_binviews.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		self._cmb_binviews.setMinimumWidth(self._cmb_binviews.fontMetrics().averageCharWidth() * 24)
		self._cmb_binviews.setMaximumWidth(self._cmb_binviews.fontMetrics().averageCharWidth() * 32)
		self._cmb_binviews.addItem("")
		self._cmb_binviews.insertSeparator(1)
		self.addWidget(self._cmb_binviews)

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

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())

		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)

		self._section_top       = BSBinContentsTopWidgetBar()
		self._tree_bin_contents = bintreeview.BSBinTreeView()
		self._section_bottom    = QtWidgets.QWidget()
		self._section_bottom.setLayout(QtWidgets.QHBoxLayout())

		self.layout().addWidget(self._section_top)
		self.layout().addWidget(self._tree_bin_contents)
		self.layout().addWidget(self._section_bottom)

		self._section_bottom.layout().setContentsMargins(2,2,2,2)


	def treeView(self) -> bintreeview.BSBinTreeView:
		"""Get the main view"""
		return self._tree_bin_contents
	
	def setTreeView(self, treeview:bintreeview.BSBinTreeView):
		self._tree_bin_contents = treeview
	
	def topWidgetBar(self) -> BSBinContentsTopWidgetBar:
		return self._section_top
	
	def setTopWidgetBar(self, toolbar:BSBinContentsTopWidgetBar):
		self._section_top = toolbar
	
	def bottomWidgetBar(self) -> BSBinContentsWidgetBar:
		return self._section_bottom
	
	def setBottomWidgetBar(self, widget:BSBinContentsWidgetBar):
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
		self._tree_bin_contents.setFont(bin_font)

	@QtCore.Slot()
	def _connectSourceModelSlots(self):

		source_model = self._tree_bin_contents.model().sourceModel()

		if not source_model:
			return
		
		source_model.rowsInserted.connect(self.updateBinStats)
		source_model.rowsRemoved.connect(self.updateBinStats)
		source_model.modelReset.connect(self.updateBinStats)

	@QtCore.Slot()
	def updateBinStats(self):

		#print("HI")

		count_visible = self._tree_bin_contents.model().rowCount()
		count_all = self._tree_bin_contents.model().sourceModel().rowCount()
		self._lbl_bin_item_count.setText(f"Showing {QtCore.QLocale.system().toString(count_visible)} of {QtCore.QLocale.system().toString(count_all)} items")
	
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