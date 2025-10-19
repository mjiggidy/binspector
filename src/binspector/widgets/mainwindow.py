from PySide6 import QtCore, QtWidgets, QtGui
from os import PathLike
from ..managers import actions, binproperties
from ..widgets import binwidget, menus, toolboxes, buttons, about
from ..views import treeview
from ..core import binloader

class BSMainWindow(QtWidgets.QMainWindow):
	"""Main window for BinSpectre 👻"""

	sig_request_new_window        = QtCore.Signal()
	sig_request_quit_application  = QtCore.Signal()
	sig_request_show_user_folder  = QtCore.Signal()
	sig_request_check_updates     = QtCore.Signal()
	sig_request_visit_discussions = QtCore.Signal()

	sig_bin_changed               = QtCore.Signal(str)
	"""Window is loading a new bin"""

	def __init__(self):

		super().__init__()

		self._settings         = QtCore.QSettings()
		self._man_actions      = actions.ActionsManager(self)	# NOTE: Investigate ownership

		# Define managers
		self._man_binview      = binproperties.BSBinViewManager()
		self._man_siftsettings = binproperties.BSBinSiftSettingsManager()
		self._man_appearance   = binproperties.BSBinAppearanceSettingsManager()
		self._man_sorting      = binproperties.BSBinSortingPropertiesManager()
		self._man_binitems     = binproperties.BSBinItemsManager()
		self._man_bindisplay   = binproperties.BSBinDisplaySettingsManager()
		self._man_viewmode     = binproperties.BSBinViewModeManager()

		# Define signals
		self._sigs_binloader   = binloader.BSBinViewLoader.Signals()

		# Define widgets
		self._main_bincontents         = binwidget.BSBinContentsWidget()

		self._tool_bindisplay  = toolboxes.BSBinDisplaySettingsView()
		self._dock_bindisplay  = QtWidgets.QDockWidget("Bin Display Settings")
		
		self._tool_sifting     = toolboxes.BSBinSiftSettingsView()
		self._dock_sifting     = QtWidgets.QDockWidget("Sift Settings")

		self._tool_appearance  = toolboxes.BSBinAppearanceSettingsView()
		self._dock_appearance  = QtWidgets.QDockWidget("Font Colors")

		self._tool_binview     = treeview.LBTreeView()
		self._dock_binview     = QtWidgets.QDockWidget("Bin View Settings")

		self._btn_toolbox_bindisplay = buttons.LBPushButtonAction(show_text=False)
		self._btn_toolbox_appearance = buttons.LBPushButtonAction(show_text=False)
		self._btn_toolbox_sifting    = buttons.LBPushButtonAction(show_text=False)
		self._btn_toolbox_binview    = buttons.LBPushButtonAction(show_text=False)
		
		# The rest
		
		self.setMenuBar(menus.BinWindowMenuBar(self._man_actions))
		self.setupWidgets()
		self.setupDock()
		self.setupActions()
		self.setupSignals()


	def setupWidgets(self):
		"""Configure general widget placement and config"""
		
		self.setCentralWidget(self._main_bincontents)

		self._dock_bindisplay.setWidget(self._tool_bindisplay)
		self._dock_sifting.setWidget(self._tool_sifting)
		self._dock_appearance.setWidget(self._tool_appearance)
		self._dock_binview.setWidget(self._tool_binview)
		
		self._dock_bindisplay.hide()
		self._dock_sifting.hide()
		self._dock_appearance.hide()
		self._dock_binview.hide()

		self._main_bincontents.listView().model().setSourceModel(self._man_binitems.viewModel())
		self._tool_binview.setModel(self._man_binview.viewModel())

		self._main_bincontents.frameView().setScene(self._man_binitems.frameScene())

		# Top binbarboy
		topbar = self._main_bincontents.topWidgetBar()
		
		topbar.setOpenBinAction(self._man_actions.fileBrowserAction())
		topbar.setReloadBinAction(self._man_actions._act_reloadcurrent)
		topbar.setStopLoadAction(self._man_actions._act_stopcurrent)
		
		topbar.setViewModeListAction(self._man_actions.viewBinAsList())
		topbar.setViewModeFrameAction(self._man_actions.viewBinAsFrame())
		topbar.setViewModeScriptAction(self._man_actions.viewBinAsScript())
		
		pol = topbar.progressBar().sizePolicy()
		pol.setRetainSizeWhenHidden(True)
		topbar.progressBar().setSizePolicy(pol)
		topbar.progressBar().setRange(0,0)
		topbar.progressBar().setHidden(True)
		


		# Bottom Display
		bottom_bar = self._main_bincontents.bottomWidgetBar()

		self._btn_toolbox_binview.setAction(self._man_actions.showBinViewSettings())
		self._btn_toolbox_bindisplay.setAction(self._man_actions.showBinDisplaySettings())
		self._btn_toolbox_appearance.setAction(self._man_actions.showBinAppearanceSettings())
		self._btn_toolbox_sifting.setAction(self._man_actions.showBinSiftSettings())
		
		
		self._btngrp_toolboxes = QtWidgets.QButtonGroup()
		self._btngrp_toolboxes.setExclusive(False)
		self._btngrp_toolboxes.addButton(self._btn_toolbox_binview)
		self._btngrp_toolboxes.addButton(self._btn_toolbox_bindisplay)
		self._btngrp_toolboxes.addButton(self._btn_toolbox_appearance)
		self._btngrp_toolboxes.addButton(self._btn_toolbox_sifting)

		lay_tbs = QtWidgets.QHBoxLayout()
		lay_tbs.setContentsMargins(0,0,0,0)
		lay_tbs.setSpacing(0)
		for btn in self._btngrp_toolboxes.buttons():
			lay_tbs.addWidget(btn)
		
		wid_tbs = QtWidgets.QWidget()
		wid_tbs.setLayout(lay_tbs)

		bottom_bar.layout().setColumnStretch(1,2)
		bottom_bar.layout().addWidget(buttons.BSPushButtonActionBar(self._btngrp_toolboxes), 0,2)
		
	def setupDock(self):
		"""Add and prepare the dock"""
		
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_binview)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_bindisplay)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_sifting)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._dock_appearance)

	def setupActions(self):
		"""Add applicable actions"""

		self.addActions(self._man_actions.applicationActionsGroup().actions())
		self.addActions(self._man_actions.fileActionsGroup().actions())
		self.addActions(self._man_actions.windowActionsGroup().actions())
		
		self.addActions(self._man_actions.showBinSettingsActionGroup().actions())
		self.addActions(self._man_actions.viewModesActionGroup().actions())

		self._man_actions._act_reloadcurrent.setVisible(False)
		self._man_actions._act_reloadcurrent.setEnabled(False)
		self._man_actions._act_stopcurrent.setVisible(False)
		self._man_actions._act_stopcurrent.setEnabled(False)

		
	def setupSignals(self):
		"""Connect signals and slots"""

		# Window/File Actions
		self._man_actions._act_filebrowser.triggered         .connect(self.showFileBrowser)
		self._man_actions._act_newwindow.triggered           .connect(self.sig_request_new_window)
		self._man_actions._act_closewindow.triggered         .connect(self.close)
		self._man_actions._act_quitapplication.triggered     .connect(self.sig_request_quit_application)
		self._man_actions._act_show_about.triggered          .connect(self.showAboutBox)

		self._man_actions._act_reloadcurrent.triggered       .connect(lambda: self.loadBinFromPath(self.windowFilePath()))
		self._man_actions._act_stopcurrent.triggered         .connect(self._sigs_binloader.requestStop)

		self._man_actions._act_check_updates.triggered       .connect(self.sig_request_check_updates)
		self._man_actions._act_open_discussions.triggered    .connect(self.sig_request_visit_discussions)

		# Toolbox Toggle Actions
		# NOTE: Dock widgets have a toggleViewAction() butuhhhhh
		self._man_actions.showBinDisplaySettings().toggled   .connect(self._dock_bindisplay.setVisible)
		self._dock_bindisplay.visibilityChanged              .connect(self._man_actions.showBinDisplaySettings().setChecked)

		self._man_actions.showBinAppearanceSettings().toggled.connect(self._dock_appearance.setVisible)
		self._dock_appearance.visibilityChanged              .connect(self._man_actions.showBinAppearanceSettings().setChecked)

		self._man_actions.showBinSiftSettings().toggled      .connect(self._dock_sifting.setVisible)
		self._dock_sifting.visibilityChanged                 .connect(self._man_actions.showBinSiftSettings().setChecked)

		self._man_actions.showBinViewSettings().toggled      .connect(self._dock_binview.setVisible)
		self._dock_binview.visibilityChanged                 .connect(self._man_actions.showBinViewSettings().setChecked)

		# User debuggy-type tools
		self._man_actions.showUserFolder().triggered         .connect(self.sig_request_show_user_folder)

		# Bin Settings Toolboxes
		self._man_bindisplay.sig_bin_display_changed         .connect(self._tool_bindisplay.setFlags)
		self._man_bindisplay.sig_bin_display_changed         .connect(self._main_bincontents.listView().model().setBinDisplayItemTypes)
		self._tool_bindisplay.sig_flags_changed              .connect(self._man_bindisplay.setBinDisplayFlags)

		self._man_appearance.sig_font_changed                .connect(self._tool_appearance.setBinFont)
		self._man_appearance.sig_palette_changed             .connect(self._tool_appearance.setBinPalette)
		self._man_appearance.sig_window_rect_changed         .connect(self._tool_appearance.setBinRect)
		self._man_appearance.sig_was_iconic_changed          .connect(self._tool_appearance.setWasIconic)

		self._man_appearance.sig_palette_changed             .connect(self._main_bincontents.setBinColors)
		self._man_appearance.sig_font_changed                .connect(self._main_bincontents.setBinFont)
		self._tool_appearance.sig_font_changed               .connect(self._man_appearance.sig_font_changed)
		self._tool_appearance.sig_palette_changed            .connect(self._main_bincontents.setBinColors)

		# Bin loader signals
		self._sigs_binloader.sig_begin_loading               .connect(self.prepareForBinLoading)
		self._sigs_binloader.sig_done_loading                .connect(self.cleanupAfterBinLoading)
		self._sigs_binloader.sig_got_exception               .connect(self.binLoadException)
		self._sigs_binloader.sig_aborted_loading             .connect(self.cleanupPartialBin)
		self._sigs_binloader.sig_got_mob_count               .connect(self._main_bincontents.topWidgetBar().progressBar().setMaximum)
		self._sigs_binloader.sig_got_mob_count               .connect(lambda: self._main_bincontents.topWidgetBar().progressBar().setFormat("Loading %v of %m mobs"))
 
		self._sigs_binloader.sig_got_display_mode            .connect(self._man_viewmode.setViewMode)
		self._sigs_binloader.sig_got_bin_display_settings    .connect(self._man_bindisplay.setBinDisplayFlags)
		self._sigs_binloader.sig_got_view_settings           .connect(self._man_binview.setBinView)
		self._sigs_binloader.sig_got_bin_appearance_settings .connect(self._man_appearance.setAppearanceSettings)
		self._sigs_binloader.sig_got_mob                     .connect(self._man_binitems.addMob)
		self._sigs_binloader.sig_got_mob                     .connect(lambda: self._main_bincontents.topWidgetBar().progressBar().setValue(self._main_bincontents.topWidgetBar().progressBar().value() + 1))

		# Inter-manager relations
		self._man_binview.sig_bin_view_changed               .connect(self._man_binitems.setBinView)
		self._man_binitems.sig_bin_view_changed              .connect(lambda bv, widths: self._main_bincontents.setBinViewName(bv.name))

		# Update display counts -- Not where where to put this
		self._man_binitems.sig_mob_count_changed             .connect(self._main_bincontents.updateBinStats)

		# Bin Contents Toolbars
		self._main_bincontents.topWidgetBar().searchBox().textChanged.connect(self._main_bincontents.listView().model().setSearchText)

		# Bin View Modes
		# TODO: Something about this feels circular compared to the other stuff I've been doing
		self._man_viewmode.sig_view_mode_changed             .connect(self._main_bincontents.setViewMode)
		self._man_viewmode.sig_view_mode_changed             .connect(lambda  vm: self._man_actions.viewModesActionGroup().actions()[int(vm)].setChecked(True))
		self._man_actions._actgrp_view_mode.triggered       . connect(lambda act: self._man_viewmode.setViewMode(self._man_actions._actgrp_view_mode.actions().index(act)))

	##
	## Getters & Setters
	##

	def setActionsManager(self, actions:actions.ActionsManager):
		raise DeprecationWarning("Let's not?")
		self._man_actions = actions
	
	def actionsManager(self) -> actions.ActionsManager:
		return self._man_actions
	
	def setSettings(self, settings:QtCore.QSettings):
		raise DeprecationWarning("Let's not?")
		self._settings = settings

	def binViewManager(self) -> binproperties.BSBinViewManager:
		return self._man_binview
	
	def siftSettingsManager(self) -> binproperties.BSBinSiftSettingsManager:
		return self._man_siftsettings
	
	def appearanceManager(self) -> binproperties.BSBinAppearanceSettingsManager:
		return self._man_appearance
	
	def sortingManager(self) -> binproperties.BSBinSortingPropertiesManager:
		return self._man_sorting
	
	def binItemsManager(self) -> binproperties.BSBinItemsManager:
		return self._man_binitems
	
	##
	## Slots
	##

	@QtCore.Slot(str)
	def prepareForBinLoading(self, bin_path:str):
		"""Bin load is about to begin. Prepare UI elements."""

		self._man_actions._act_filebrowser.setEnabled(False)
		
		self._man_actions._act_reloadcurrent.setEnabled(False)
		self._man_actions._act_reloadcurrent.setVisible(False)

		self._man_actions._act_stopcurrent.setEnabled(True)
		self._man_actions._act_stopcurrent.setVisible(True)
		
		self._man_binitems.viewModel().clear
		
		self._main_bincontents.topWidgetBar().progressBar().setFormat("Loading bin properties...")
		self._main_bincontents.topWidgetBar().progressBar().show()
		
		self.setCursor(QtCore.Qt.CursorShape.BusyCursor)
		self.setWindowFilePath(bin_path)
	
	@QtCore.Slot()
	def cleanupAfterBinLoading(self):
		"""A bin has finished loading.  Reset UI elements."""

		self._main_bincontents.topWidgetBar().progressBar().setMaximum(0)
		self._main_bincontents.topWidgetBar().progressBar().setValue(0)
		self._main_bincontents.topWidgetBar().progressBar().hide()
		
		#self._main_bincontents.treeView().resizeAllColumnsToContents()
		
		self._man_actions._act_reloadcurrent.setEnabled(True)
		self._man_actions._act_reloadcurrent.setVisible(True)

		self._man_actions._act_stopcurrent.setEnabled(False)
		self._man_actions._act_stopcurrent.setVisible(False)

		self._man_actions._act_filebrowser.setEnabled(True)

		self.sig_bin_changed.emit(self.windowFilePath())
		
		self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
		QtWidgets.QApplication.instance().alert(self)

	@QtCore.Slot()
	def cleanupPartialBin(self):
		"""Do any cleanup for a cancelled bin load"""

		import logging
		logging.getLogger(__name__).info("User cancelled loading bin")

	@QtCore.Slot(object)
	def binLoadException(self, exception:Exception):
		print(f"Bin load error:", exception)
	
	@QtCore.Slot()
	@QtCore.Slot(object)
	def showFileBrowser(self, initial_path:PathLike|None=None):
		"""Show the file browser to select a bin"""

		file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
			parent=self,
			caption = "Choose an Avid bin...",
			filter="Avid Bin (*.avb);;All Files (*)",
			dir=initial_path or self.windowFilePath()
		)
		
		if file_path:
			self.loadBinFromPath(file_path)

	@QtCore.Slot(object)
	def loadBinFromPath(self, bin_path:PathLike):
		"""Load a bin from the given path"""

		QtCore.QThreadPool.globalInstance().start(
			binloader.BSBinViewLoader(bin_path, self._sigs_binloader)
		)

	@QtCore.Slot()
	def showAboutBox(self):
		"""Show the About thing"""

		dlg_about = about.BSAboutDialog()
		dlg_about.exec()