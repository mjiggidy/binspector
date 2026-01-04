from os import PathLike

from PySide6 import QtCore, QtWidgets

from ..binwidget import binwidget
from ..managers import actions, binproperties, appearance
from ..widgets import siftwidget, menus, toolboxes, buttons, about
from ..views import treeview
from ..core import binloader, icon_engines, icon_providers

class BSMainWindow(QtWidgets.QMainWindow):
	"""Main window for BinSpectre 👻"""

	sig_request_new_window        = QtCore.Signal()
	sig_request_quit_application  = QtCore.Signal()
	sig_request_show_user_folder  = QtCore.Signal()
	sig_request_show_log_viewer   = QtCore.Signal()
	sig_request_show_settings     = QtCore.Signal()
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
		self._man_appearance   = appearance.BSBinAppearanceSettingsManager()
		self._man_sorting      = binproperties.BSBinSortingPropertiesManager()
		self._man_binitems     = binproperties.BSBinItemsManager()
		self._man_bindisplay   = binproperties.BSBinDisplaySettingsManager()
		self._man_viewmode     = binproperties.BSBinViewModeManager()

		# Define signals
		self._queue_size       = 500  # Mobs to batch-load
		self._use_animation    = True # Use animated progress bar
		self._sigs_binloader   = binloader.BSBinViewLoader.Signals()

		# Define animators
		self._anim_progress    = QtCore.QPropertyAnimation(parent=self)
		self._time_last_chunk  = QtCore.QElapsedTimer()
		self._time_last_load   = QtCore.QElapsedTimer()

		# Define widgets
		self._bin_widget = binwidget.BSBinContentsWidget()

		self._tool_bindisplay  = toolboxes.BSBinDisplaySettingsView()
		self._dock_bindisplay  = QtWidgets.QDockWidget(self.tr("Bin Display Settings"))
		
		self._tool_sifting     = siftwidget.BSSiftSettingsWidget()
		self._dock_sifting     = QtWidgets.QDockWidget(self.tr("Sift Settings"))

		self._tool_appearance  = toolboxes.BSBinAppearanceSettingsView()
		self._dock_appearance  = QtWidgets.QDockWidget(self.tr("Font & Colors"))

		self._tool_binview     = treeview.BSTreeViewBase()
		self._dock_binview     = QtWidgets.QDockWidget(self.tr("Bin View Settings"))

		self._btn_toolbox_bindisplay = buttons.BSActionPushButton(show_text=False)
		self._btn_toolbox_appearance = buttons.BSActionPushButton(show_text=False)
		self._btn_toolbox_sifting    = buttons.BSActionPushButton(show_text=False)
		self._btn_toolbox_binview    = buttons.BSActionPushButton(show_text=False)


		# The rest
		
		self.setMenuBar(menus.BinWindowMenuBar(self._man_actions))
		self.setupWidgets()
		self.setupDock()
		self.setupActions()
		self.setupSignals()


	def setupWidgets(self):
		"""Configure general widget placement and config"""
		
		self.setCentralWidget(self._bin_widget)

		self._dock_bindisplay.setWidget(self._tool_bindisplay)
		self._dock_sifting.setWidget(self._tool_sifting)
		self._dock_appearance.setWidget(self._tool_appearance)
		self._dock_binview.setWidget(self._tool_binview)
		
		self._dock_bindisplay.hide()
		self._dock_sifting.hide()
		self._dock_appearance.hide()
		self._dock_binview.hide()

		self._bin_widget.setBinModel(self._man_binitems.viewModel())
		
		self._tool_binview.setModel(self._man_binview.viewModel())

		#self._main_bincontents.frameView().setScene(self._man_binitems.frameScene())

		# Top binbarboy
		topbar = self._bin_widget.topWidgetBar()
		
		topbar.setOpenBinAction(self._man_actions.fileBrowserAction())
		topbar.setReloadBinAction(self._man_actions._act_reloadcurrent)
		topbar.setStopLoadAction(self._man_actions._act_stopcurrent)
		
		topbar.setViewModeListAction(self._man_actions.viewBinAsList())
		topbar._btn_viewmode_list.setIconEngine(icon_providers.getPalettedIconEngine(self._man_actions._act_view_list))

		topbar.setViewModeFrameAction(self._man_actions.viewBinAsFrame())
		topbar._btn_viewmode_frame.setIconEngine(icon_providers.getPalettedIconEngine(self._man_actions._act_view_frame))

		topbar.setViewModeScriptAction(self._man_actions.viewBinAsScript())
		topbar._btn_viewmode_script.setIconEngine(icon_providers.getPalettedIconEngine(self._man_actions._act_view_script))

		self._anim_progress.setTargetObject(topbar.progressBar())
		self._anim_progress.setPropertyName(QtCore.QByteArray.fromStdString("value"))
		self._anim_progress.setEasingCurve(QtCore.QEasingCurve.Type.Linear)

		grp = QtWidgets.QSizeGrip(self._bin_widget.listView())
		self._bin_widget.listView().setCornerWidget(grp)
		
		# Apply Bin Settings Toggles
		for act_toggle in reversed(self._man_actions.toggleBinSettingsActionGroup().actions()):	
			
			btn = buttons.BSPalettedActionPushButton(act_toggle, show_text=False, icon_engine=icon_providers.getPalettedIconEngine(act_toggle))
			btn.setIconSize(QtCore.QSize(8,8))
			btn.setFixedSize(QtCore.QSize(
				*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
			))
			self._bin_widget.scrollbarScaler().sig_size_changed.connect(
				lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
			)
			
			self._bin_widget.listView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)

		# Frame View Toggles
		btn = buttons.BSPalettedActionPushButton(self._man_actions._act_toggle_sys_appearance, show_text=False, icon_engine=icon_providers.getPalettedIconEngine(self._man_actions._act_toggle_sys_appearance))
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedSize(QtCore.QSize(
			*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
		))
		self._bin_widget.scrollbarScaler().sig_size_changed.connect(
			lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
		)

		self._bin_widget.frameView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)

		btn = buttons.BSPalettedActionPushButton(self._man_actions._act_toggle_show_all_items, show_text=False, icon_engine=icon_engines.BSPalettedSvgIconEngine(":/icons/gui/toggle_frame_showall.svg"))
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedSize(QtCore.QSize(
			*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
		))
		self._bin_widget.scrollbarScaler().sig_size_changed.connect(
			lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
		)

		self._bin_widget.frameView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)

		for act_toggle in self._bin_widget.frameView().actions().overlayActions().actions(): #lol

			btn = buttons.BSPalettedActionPushButton(act_toggle, show_text=False, icon_engine=icon_providers.getPalettedIconEngine(act_toggle))
			btn.setIconSize(QtCore.QSize(8,8))
			btn.setFixedSize(QtCore.QSize(
				*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
			))
			self._bin_widget.scrollbarScaler().sig_size_changed.connect(
				lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
			)
			
			self._bin_widget.frameView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)			


		
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

		self.addActions(self._man_actions.toggleBinSettingsActionGroup().actions())

		self._man_actions._act_reloadcurrent.setVisible(False)
		self._man_actions._act_reloadcurrent.setEnabled(False)
		self._man_actions._act_stopcurrent  .setVisible(False)
		self._man_actions._act_stopcurrent  .setEnabled(False)
		
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
		# NOTE: Have application instance hook directly into window.actionsManager()?
		# NOTE FROM FUTURE SELF: ^^ what?
		self._man_actions.showUserFolder().triggered         .connect(self.sig_request_show_user_folder)
		self._man_actions.showLogViewer().triggered          .connect(self.sig_request_show_log_viewer)
		self._man_actions.showSettingsWindow().triggered     .connect(self.sig_request_show_settings)

		# Bin Settings Toolboxes
		self._man_bindisplay.sig_bin_display_changed         .connect(self._tool_bindisplay.setFlags)
		self._man_bindisplay.sig_bin_display_changed         .connect(self._bin_widget.listView().model().setBinDisplayItemTypes)
		self._tool_bindisplay.sig_flags_changed              .connect(self._man_bindisplay.setBinDisplayFlags)

		# Appearance to binwidget
		self._man_appearance.sig_font_changed                .connect(self._bin_widget.setBinFont)
		self._man_appearance.sig_palette_changed             .connect(self._bin_widget.setBinPalette)
		
		# Appearance to toolbox
		self._man_appearance.sig_bin_font_changed            .connect(self._tool_appearance.setBinFont)
		self._man_appearance.sig_bin_colors_changed          .connect(self._tool_appearance.setBinColors)
		self._man_appearance.sig_window_rect_changed         .connect(self._tool_appearance.setBinRect)
		self._man_appearance.sig_was_iconic_changed          .connect(self._tool_appearance.setWasIconic)

		# Toolbox to Appearance
		self._tool_appearance.sig_font_changed               .connect(self._man_appearance.setBinFont)
		self._tool_appearance.sig_colors_changed             .connect(self._man_appearance.setBinColors)

		# Bin loader signals
		self._sigs_binloader.sig_begin_loading               .connect(self.prepareForBinLoading)
		self._sigs_binloader.sig_done_loading                .connect(self.cleanupAfterBinLoading)
		self._sigs_binloader.sig_got_exception               .connect(self.binLoadException)
		self._sigs_binloader.sig_aborted_loading             .connect(self.cleanupPartialBin)
		self._sigs_binloader.sig_got_mob_count               .connect(self._bin_widget.topWidgetBar().progressBar().setMaximum)
		self._sigs_binloader.sig_got_mob_count               .connect(lambda: self._bin_widget.topWidgetBar().progressBar().setFormat(self.tr("Loading %v of %m mobs", "%v=current_count; %m=total_count")))
		#self._sigs_binloader.sig_got_mob_count               .connect(lambda: self.updateLoadingBar([]))
 
		self._sigs_binloader.sig_got_display_mode            .connect(self._man_viewmode.setViewMode)
		self._sigs_binloader.sig_got_bin_display_settings    .connect(self._man_bindisplay.setBinDisplayFlags)
		self._sigs_binloader.sig_got_view_settings           .connect(self._man_binview.setBinView)
		self._sigs_binloader.sig_got_sort_settings           .connect(self._man_binview.setDefaultSortColumns)
		self._sigs_binloader.sig_got_bin_appearance_settings .connect(self._man_appearance.setAppearanceSettings)
		self._sigs_binloader.sig_got_mobs                    .connect(self._man_binitems.addMobs, QtCore.Qt.ConnectionType.BlockingQueuedConnection) # These fellas pile up
		#self._sigs_binloader.sig_got_mobs.connect(print)
		self._sigs_binloader.sig_got_mobs                    .connect(self.updateLoadingBar, QtCore.Qt.ConnectionType.BlockingQueuedConnection)
		#self._sigs_binloader.sig_got_mob                    .connect(self._man_binitems.addMob)
		#self._sigs_binloader.sig_got_mob                    .connect(lambda: self._main_bincontents.topWidgetBar().progressBar().setValue(self._main_bincontents.topWidgetBar().progressBar().value() + 1))

		self._sigs_binloader.sig_got_sift_settings           .connect(self._man_siftsettings.setSiftSettings)
		self._man_siftsettings.sig_bin_view_changed          .connect(self._tool_sifting.setBinView)
		self._man_siftsettings.sig_sift_settings_changed     .connect(self._tool_sifting.setSiftOptions)
		self._man_siftsettings.sig_sift_enabled              .connect(self._tool_sifting.setSiftEnabled)
		self._man_siftsettings.sig_sift_enabled              .connect(self._bin_widget.setSiftEnabled)
		self._man_siftsettings.sig_sift_settings_changed     .connect(self._bin_widget.setSiftOptions)
		self._tool_sifting.sig_options_set                   .connect(self._man_siftsettings.setSiftSettings)

		# Inter-manager relations
		self._man_binview.sig_bin_view_changed               .connect(self._man_binitems.setBinView)
		self._man_binview.sig_bin_view_changed               .connect(self._man_siftsettings.setBinView)
		self._man_binview.sig_bin_view_changed               .connect(self._bin_widget.setBinView)
		#self._man_binview.sig_bin_view_changed               .connect(self._bin_widget.listView().)

		# Update display counts -- Not where where to put this
		self._man_binitems.sig_mob_count_changed             .connect(self._bin_widget.updateBinStats)

		# Bin Contents Toolbars
		self._bin_widget.topWidgetBar().searchBox().textChanged.connect(self._bin_widget.listView().model().setSearchText)

		#self._main_bincontents.sig_bin_palette_changed.connect(self._man_actions._palette_watcher.setPalette)

		# Bin View Modes
		# TODO: Something about this feels circular compared to the other stuff I've been doing
		self._man_viewmode.sig_view_mode_changed                .connect(self._bin_widget.setViewMode)
		self._man_viewmode.sig_view_mode_changed                .connect(lambda  vm: self._man_actions.viewModesActionGroup().actions()[int(vm)].setChecked(True))
		self._man_actions._actgrp_view_mode.triggered           .connect(lambda act: self._man_viewmode.setViewMode(self._man_actions._actgrp_view_mode.actions().index(act)))

		# Bin Settings Toggles
		self._man_actions._act_toggle_show_all_columns.toggled  .connect(self._man_binview.setAllColumnsVisible)
		self._man_binview.sig_all_columns_toggled               .connect(self._man_actions._act_toggle_show_all_columns.setChecked)
		self._man_binview.sig_view_mode_toggled                 .connect(self._bin_widget.setBinViewEnabled)
		
		self._man_actions._act_toggle_show_all_items.toggled    .connect(self._man_binview.setAllItemsVisible)
		self._man_binview.sig_all_items_toggled                 .connect(self._man_actions._act_toggle_show_all_items.setChecked)
		self._man_binview.sig_bin_filters_toggled               .connect(self._bin_widget.setBinFiltersEnabled)
		self._man_binview.sig_focus_bin_column                  .connect(self._bin_widget.focusBinColumn)

		self._man_actions._act_toggle_sys_appearance.toggled    .connect(self._man_appearance.setUseSystemAppearance)
		self._man_appearance.sig_use_system_appearance_toggled  .connect(self._man_actions._act_toggle_sys_appearance.setChecked)
		
		self._tool_binview.activated                            .connect(self._man_binview.requestFocusColumn)

	##
	## Getters & Setters
	##
	
	def actionsManager(self) -> actions.ActionsManager:
		return self._man_actions

	def binViewManager(self) -> binproperties.BSBinViewManager:
		return self._man_binview
	
	def siftSettingsManager(self) -> binproperties.BSBinSiftSettingsManager:
		return self._man_siftsettings
	
	def appearanceManager(self) -> appearance.BSBinAppearanceSettingsManager:
		return self._man_appearance
	
	def sortingManager(self) -> binproperties.BSBinSortingPropertiesManager:
		return self._man_sorting
	
	def binItemsManager(self) -> binproperties.BSBinItemsManager:
		return self._man_binitems
	
	def binLoadingSignalManger(self) -> binloader.BSBinViewLoader.Signals:
		return self._sigs_binloader
	
	def binContentsWidget(self) -> binwidget.BSBinContentsWidget:
		return self._bin_widget

	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):
		self._queue_size = queue_size

	def mobQueueSize(self) -> int:
		return self._queue_size
	
	@QtCore.Slot(bool)
	def setUseAnimation(self, use_animation:bool):
		self._use_animation = use_animation
	
	def useAnimation(self) -> bool:
		"""Use fancy animated progress bar"""

		return self._use_animation
	
	##
	## Slots
	##

	@QtCore.Slot(str)
	def prepareForBinLoading(self, bin_path:str):
		"""Bin load is about to begin. Prepare UI elements."""

		import logging
		logging.getLogger(__name__).info("Begin loading %s", bin_path)
		
		self._time_last_load.start()

		self._man_actions._act_filebrowser.setEnabled(False)
		
		self._man_actions._act_reloadcurrent.setEnabled(False)
		self._man_actions._act_reloadcurrent.setVisible(False)

		self._man_actions._act_stopcurrent.setEnabled(True)
		self._man_actions._act_stopcurrent.setVisible(True)
		
		self._man_binitems.viewModel().clear()
		
		self._bin_widget.topWidgetBar().progressBar().setFormat(self.tr("Loading bin properties..."))
		self._bin_widget.topWidgetBar().progressBar().show()

		self._bin_widget.listView().setSortingEnabled(False)
		self._bin_widget.listView().model().setDynamicSortFilter(False)
		
		self.setCursor(QtCore.Qt.CursorShape.BusyCursor)
		self.setWindowFilePath(bin_path)

	@QtCore.Slot(object)
	def updateLoadingBar(self, mobs_list:list):
		"""Update/animate the progress"""

		if self._use_animation:

			last_duration     = self._time_last_chunk.restart() if self._time_last_chunk.isValid() else 5_000
			adjusted_duration = round(last_duration * (len(mobs_list)/self._queue_size))

			self._anim_progress.stop()
			self._anim_progress.setStartValue(self._anim_progress.targetObject().value())
			#self._anim_progress.setEndValue(min(self._anim_progress.targetObject().value() + self._queue_size, self._anim_progress.targetObject().maximum()))
			self._anim_progress.setEndValue((self._anim_progress.endValue() or 0) + len(mobs_list))
			self._anim_progress.setDuration(adjusted_duration)
			
			if not self._time_last_chunk.isValid():
				self._time_last_chunk.start()
			
			#print(adjusted_duration)
			
			#print(adjusted_duration)
			#import logging
			#logging.getLogger(__name__).debug("Restart animation: start=%s, end=%s, duration=%s", self._anim_progress.startValue(), self._anim_progress.endValue(), self._anim_progress.duration())
			self._anim_progress.start()
		else:
			self._bin_widget.topWidgetBar().progressBar().setValue(self._bin_widget.topWidgetBar().progressBar().value() + len(mobs_list))
	
	@QtCore.Slot()
	def cleanupAfterBinLoading(self):
		"""A bin has finished loading.  Reset UI elements."""

		# NOTE: If I really wanna tween the last of the progress,
		# I could do something like below. But is it necessary?
		# PROBABLY NOT.
		#self._anim_progress.finished.connect(self.cleanupProgressBar)

		# NOTE: Otherwise, I'm just resetting everything immediately which I think is the way to go
		self._anim_progress.stop()
		self._anim_progress.setEndValue(0)
		self._time_last_chunk.invalidate()


		self._bin_widget.topWidgetBar().progressBar().setMaximum(0)
		self._bin_widget.topWidgetBar().progressBar().setValue(0)
		self._bin_widget.topWidgetBar().progressBar().hide()

		# Enabling sorting also performs a sort... sooo
		# Set invalid sort column first, per the docs
		# TODO: Set as stored sort column if available from the bin
		self._bin_widget.listView().header().setSortIndicator(-1, QtCore.Qt.SortOrder.AscendingOrder)
		self._bin_widget.listView().setSortingEnabled(True)
		self._bin_widget.listView().model().setDynamicSortFilter(True)

		for col in range(self._bin_widget.listView().header().count()):
			print("Haha...")
			self._bin_widget.listView().setColumnWidthFromBinView(col, True)
		
		if self._man_binview.defaultSortColumns():
			last_col = self._man_binview.defaultSortColumns()[-1]
			direction, column_name = QtCore.Qt.SortOrder(last_col[0]), last_col[1]
			if column_name in self._bin_widget.listView().columnDisplayNames():
				self._bin_widget.listView().header().setSortIndicator(
					self._bin_widget.listView().columnDisplayNames().index(column_name),
					direction
				)
		
		self._man_actions._act_reloadcurrent.setEnabled(True)
		self._man_actions._act_reloadcurrent.setVisible(True)

		self._man_actions._act_stopcurrent.setEnabled(False)
		self._man_actions._act_stopcurrent.setVisible(False)

		self._man_actions._act_filebrowser.setEnabled(True)

		self.sig_bin_changed.emit(self.windowFilePath())
		
		self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
		QtWidgets.QApplication.instance().alert(self)

		total_load_time = self._time_last_load.elapsed()
		self._time_last_load.invalidate()
		import logging
		logging.getLogger(__name__).info("Finished loading %s in %s seconds (queuesize=%s, fancy=%s)", self.windowFilePath(), round(total_load_time/1000,2), self._queue_size, self._use_animation)

	@QtCore.Slot()
	@QtCore.Slot(str)
	def cleanupPartialBin(self, message:str|None=None):
		"""Do any cleanup for a cancelled bin load"""

		import logging
		logging.getLogger(__name__).warning("Aborted loading bin")
		
		if message:
			QtWidgets.QMessageBox.critical(self, self.tr("Bin Not Loaded"), message)



	@QtCore.Slot(object)
	def binLoadException(self, exception:Exception):

		import logging
		logging.getLogger(__name__).error(exception)
	
	@QtCore.Slot()
	@QtCore.Slot(object)
	def showFileBrowser(self, initial_path:PathLike|None=None):
		"""Show the file browser to select a bin"""

		file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
			parent=self,
			caption = self.tr("Choose an Avid bin..."),
			filter=self.tr("Avid Bin (*.avb);;All Files (*)"),
			dir=initial_path or self.windowFilePath()
		)

		self.activateWindow()
		
		if file_path:
			self.loadBinFromPath(file_path)

	@QtCore.Slot(object)
	def loadBinFromPath(self, bin_path:PathLike):
		"""Load a bin from the given path"""

		QtCore.QThreadPool.globalInstance().start(
			binloader.BSBinViewLoader(bin_path, self._sigs_binloader, self._queue_size)
		)

	@QtCore.Slot()
	def showAboutBox(self):
		"""Show the About thing"""

		dlg_about = about.BSAboutDialog()
		dlg_about.exec()

	@QtCore.Slot()
	def cleanupSignals(self):
		"""Disconnect from worker signals on close"""

		import logging
		logging.getLogger(__name__).debug("Cleaning up signals")
		
		self._sigs_binloader.requestStop()
		self._sigs_binloader.disconnect(self)

	def closeEvent(self, event):
		
		self.cleanupSignals()
		
		return super().closeEvent(event)