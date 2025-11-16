"""
Actions
"""

from PySide6 import QtCore, QtGui, QtWidgets
from ..core import icons
from ..res import icons_gui

class ActionsManager(QtCore.QObject):
	"""General actions"""

	def __init__(self, parent:QtWidgets.QWidget|None=None, palette_watcher:icons.BSPaletteWatcherForSomeReason|None=None):


		self._parent = parent or self
		super().__init__(parent=parent)

		# Palette watcher for icons
		# Which totally belongs in QActions totally yeah

		self._palette_watcher = palette_watcher or icons.BSPaletteWatcherForSomeReason()

		# File actions
		self._act_filebrowser = QtGui.QAction(self.tr("&Open Bin..."))
		"""Request file browser to choose new bin"""
		self._act_filebrowser.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
		self._act_filebrowser.setToolTip(self.tr("Choose a bin to open"))
		self._act_filebrowser.setShortcut(QtGui.QKeySequence.StandardKey.Open)

		self._act_reloadcurrent = QtGui.QAction(self.tr("&Reload Current Bin"))
		self._act_reloadcurrent.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		self._act_reloadcurrent.setToolTip(self.tr("Reload the current bin"))
		self._act_reloadcurrent.setShortcut(QtGui.QKeySequence.StandardKey.Refresh)

		self._act_stopcurrent = QtGui.QAction(self.tr("Stop Loading Bin"))
		self._act_stopcurrent.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ProcessStop))
		self._act_stopcurrent.setToolTip(self.tr("Stop loading the current bin"))
		self._act_stopcurrent.setShortcut(QtGui.QKeySequence.StandardKey.Cancel)


		# Window actions
		self._act_newwindow = QtGui.QAction(self.tr("&New Window..."))
		"""Request new bin window"""
		self._act_newwindow.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowNew))
		self._act_newwindow.setToolTip(self.tr("Open a new window"))
		self._act_newwindow.setShortcut(QtGui.QKeySequence.StandardKey.New)


		self._act_closewindow = QtGui.QAction(self.tr("Close &Window"))
		"""Close active bin window"""
		self._act_closewindow.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowClose))
		self._act_closewindow.setToolTip(self.tr("Close this window"))
		self._act_closewindow.setShortcut(QtGui.QKeySequence.StandardKey.Close)


		# Application actions
		self._act_show_settings = QtGui.QAction(self.tr("Settings..."))
		"""Open Settings window"""
		self._act_show_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.InsertImage))
		self._act_show_settings.setToolTip(self.tr("Open {application_name} settings").format(application_name=QtWidgets.QApplication.instance().applicationName()))
		self._act_show_settings.setShortcut(QtGui.QKeySequence.StandardKey.Preferences)
		self._act_show_settings.setMenuRole(QtGui.QAction.MenuRole.PreferencesRole)

		self._act_quitapplication = QtGui.QAction(self.tr("&Quit"))
		"""Quit application"""
		self._act_quitapplication.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ApplicationExit))
		self._act_quitapplication.setToolTip(self.tr("Quit {application_name}").format(application_name=QtWidgets.QApplication.instance().applicationName()))
		self._act_quitapplication.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
		self._act_quitapplication.setMenuRole(QtGui.QAction.MenuRole.QuitRole)


		# View modes
		self._act_view_list   = QtGui.QAction(self.tr("List View"), checkable=True, checked=True, parent=self._parent)
		"""Toggle Bin View Mode: List"""
		icon_engine = icons.BSPalettedSvgIconEngine(":/icons/gui/view_list.svg", self._palette_watcher)
		self._act_view_list.setIcon(QtGui.QIcon(icon_engine))
		self._act_view_list.setShortcut(QtGui.QKeySequence(QtGui.Qt.Modifier.CTRL|QtGui.Qt.Key.Key_1))
		self._act_view_list.setToolTip(self.tr("Show items in list view mode"))

		self._act_view_frame  = QtGui.QAction(self.tr("Frame View"), checkable=True, parent=self._parent)
		"""Toggle Bin View Mode: Frame"""
		icon_engine = icons.BSPalettedSvgIconEngine(":/icons/gui/view_frame.svg", self._palette_watcher)
		self._act_view_frame.setIcon(QtGui.QIcon(icon_engine))
		self._act_view_frame.setShortcut(QtGui.QKeySequence(QtGui.Qt.Modifier.CTRL|QtGui.Qt.Key.Key_2))
		self._act_view_frame.setToolTip(self.tr("Show items in frame view mode"))

		self._act_view_script = QtGui.QAction(self.tr("Script View"), checkable=True, parent=self._parent)
		"""Toggle Bin View Mode: Script"""
		icon_engine = icons.BSPalettedSvgIconEngine(":/icons/gui/view_script.svg", self._palette_watcher)
		self._act_view_script.setIcon(QtGui.QIcon(icon_engine))
		self._act_view_script.setShortcut(QtGui.QKeySequence(QtGui.Qt.Modifier.CTRL|QtGui.Qt.Key.Key_3))
		self._act_view_script.setToolTip(self.tr("Show items in script view mode"))


		# Bin settings
		self._act_toggle_bindisplay_settings  = QtGui.QAction(self.tr("Show Bin Display Settings"), checkable=True, parent=self._parent)
		"""Toggle visibility of Bin Display Settings toolbox"""
		self._act_toggle_bindisplay_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentPageSetup))

		self._act_toggle_binview_settings    = QtGui.QAction(self.tr("Show Bin View Settings"), checkable=True, parent=self._parent)
		"""Toggle visibility of Binview Settings toolbox"""
		self._act_toggle_binview_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRestore))
		
		self._act_toggle_appearance_options = QtGui.QAction(self.tr("Show Appearance Settings"), checkable=True, parent=self._parent)
		"""Toggle visibility of Fonts & Colors toolbox"""
		self._act_toggle_appearance_options.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.Battery))

		self._act_toggle_sift_settings = QtGui.QAction(self.tr("Show Sift Settings"), checkable=True, parent=self._parent)
		"""Toggle visibility of Sift Settings toolbox"""
		self._act_toggle_sift_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AudioVolumeHigh))


		# Bin Visibility Toggles
		self._act_toggle_use_binview = QtGui.QAction(self.tr("Toggle Bin View"))
		self._act_toggle_use_binview.setCheckable(True)
		self._act_toggle_use_binview.setToolTip(self.tr("Toggle between columns shown in the bin view, and all columns available"))
		self._act_toggle_use_binview.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_1))
		self._act_toggle_use_binview.setIcon(QtGui.QIcon(icons.BSPalettedSvgIconEngine(":/icons/gui/toggle_columns.svg", self._palette_watcher)))

		self._act_toggle_use_binfilters = QtGui.QAction(self.tr("Toggle Bin Item Filters"))
		self._act_toggle_use_binfilters.setCheckable(True)
		self._act_toggle_use_binfilters.setToolTip(self.tr("Toggle between filtering bin items, and showing all items in the bin"))
		self._act_toggle_use_binfilters.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_2))
		self._act_toggle_use_binfilters.setIcon(QtGui.QIcon(icons.BSPalettedSvgIconEngine(":/icons/gui/toggle_rows.svg", self._palette_watcher)))

		self._act_toggle_use_binappearance = QtGui.QAction(self.tr("Toggle Bin Appearance Settings"))
		self._act_toggle_use_binappearance.setCheckable(True)
		self._act_toggle_use_binappearance.setToolTip(self.tr("Toggle between saved fonts and colors, and default system appearance"))
		self._act_toggle_use_binappearance.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_3))
		self._act_toggle_use_binappearance.setIcon(QtGui.QIcon(icons.BSPalettedSvgIconEngine(":/icons/gui/toggle_appearance.svg", self._palette_watcher)))


		# Tools
		self._act_show_local_storage = QtGui.QAction(self.tr("Open User Data Folder"), parent=self._parent)
		"""Open local storage"""
		self._act_show_local_storage.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen))

		self._act_show_log_viewer = QtGui.QAction(self.tr("Show Log Viewer"), parent=self._parent)
		"""Show the log viewer window"""
		self._act_show_log_viewer.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
		self._act_show_log_viewer.setToolTip(self.tr("Show the log viewer window"))
		self._act_show_log_viewer.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.Key.Key_L))
	

		# Help menu stuff
		self._act_open_discussions = QtGui.QAction(self.tr("Visit Discussion Board..."), parent=self._parent)
		self._act_open_discussions.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DialogInformation))

		self._act_check_updates = QtGui.QAction(self.tr("Check For Updates..."), parent=self._parent)
		self._act_check_updates.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SoftwareUpdateAvailable))
		self._act_check_updates.setMenuRole(QtGui.QAction.MenuRole.ApplicationSpecificRole)

		self._act_show_about = QtGui.QAction(self.tr("About {application_name}...").format(application_name=QtWidgets.QApplication.instance().applicationDisplayName()), parent=self._parent)
		"""Show About Box"""
		self._act_show_about.setMenuRole(QtGui.QAction.MenuRole.AboutRole)
		self._act_show_about.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.HelpAbout))


		# Action Groups
		self._actgrp_file = QtGui.QActionGroup(self._parent)
		self._actgrp_file.addAction(self._act_filebrowser)
		self._actgrp_file.addAction(self._act_reloadcurrent)
		self._actgrp_file.addAction(self._act_stopcurrent)
		
		self._actgrp_window = QtGui.QActionGroup(self._parent)
		self._actgrp_window.addAction(self._act_newwindow)
		self._actgrp_window.addAction(self._act_closewindow)

		self._actgrp_app = QtGui.QActionGroup(self._parent)
		self._actgrp_app.addAction(self._act_quitapplication)
		self._actgrp_app.addAction(self._act_show_about)
		self._actgrp_app.addAction(self._act_show_settings)

		self._actgrp_view_mode = QtGui.QActionGroup(self._parent)
		self._actgrp_view_mode.setExclusive(True)
		self._actgrp_view_mode.addAction(self._act_view_list)
		self._actgrp_view_mode.addAction(self._act_view_frame)
		self._actgrp_view_mode.addAction(self._act_view_script)

		self._actgrp_bin_settings = QtGui.QActionGroup(self._parent)
		self._actgrp_bin_settings.setExclusive(False)  # Doesn't always default??
		self._actgrp_bin_settings.addAction(self._act_toggle_binview_settings)
		self._actgrp_bin_settings.addAction(self._act_toggle_bindisplay_settings)
		self._actgrp_bin_settings.addAction(self._act_toggle_appearance_options)
		self._actgrp_bin_settings.addAction(self._act_toggle_sift_settings)

		self._actgrp_user_tools = QtGui.QActionGroup(self._parent)
		self._actgrp_user_tools.addAction(self._act_show_local_storage)
		self._actgrp_user_tools.addAction(self._act_show_log_viewer)

		self._actgrp_toggle_binsettings = QtGui.QActionGroup(self._parent)
		self._actgrp_toggle_binsettings.setExclusive(False)
		self._actgrp_toggle_binsettings.addAction(self._act_toggle_use_binview)
		self._actgrp_toggle_binsettings.addAction(self._act_toggle_use_binfilters)
		self._actgrp_toggle_binsettings.addAction(self._act_toggle_use_binappearance)
	
	def applicationActionsGroup(self) -> QtGui.QActionGroup:
		"""Application-wide actions"""

		return self._actgrp_app

	def fileActionsGroup(self) -> QtGui.QActionGroup:
		"""File operation actions"""

		return self._actgrp_file

	def windowActionsGroup(self) -> QtGui.QActionGroup:
		"""Window actions"""

		return self._actgrp_window

	def viewModesActionGroup(self) -> QtGui.QActionGroup:
		"""Actions for toggling between bin view modes"""

		return self._actgrp_view_mode
	
	def showBinSettingsActionGroup(self) -> QtGui.QActionGroup:
		"""Actions for toggling display of settings toolboxes"""

		return self._actgrp_bin_settings
	
	def userToolsActionsGroup(self) -> QtGui.QActionGroup:
		"""Debug-y user stuff"""

		return self._actgrp_user_tools

	def showAboutBoxAction(self) -> QtGui.QAction:
		"""Show the About Box"""

		return self._act_show_about
	
	def showSettingsWindow(self) -> QtGui.QAction:
		"""Show the Settings window"""

		return self._act_show_settings

	def fileBrowserAction(self) -> QtGui.QAction:
		"""User requests file browser"""

		return self._act_filebrowser

	def newWindowAction(self) -> QtGui.QAction:
		"""User requests new window"""

		return self._act_newwindow

	def closeWindowAction(self) -> QtGui.QAction:
		"""Close the current window"""

		return self._act_closewindow

	def quitApplicationAction(self) -> QtGui.QAction:
		"""Quit the application"""

		return self._act_quitapplication
	
	def viewBinAsList(self) -> QtGui.QAction:
		"""Set bin view to List"""
		
		return self._act_view_list
	
	def viewBinAsFrame(self) -> QtGui.QAction:
		"""Set bin view to Frame"""
		
		return self._act_view_frame
	
	def viewBinAsScript(self) -> QtGui.QAction:
		"""Set bin view to Script"""
		
		return self._act_view_script
	
	def showBinDisplaySettings(self) -> QtGui.QAction:
		"""Show bin display settings"""

		return self._act_toggle_bindisplay_settings
	
	def showBinViewSettings(self) -> QtGui.QAction:
		"""Show bin view settings"""

		return self._act_toggle_binview_settings
	
	def showBinAppearanceSettings(self) -> QtGui.QAction:
		"""Show bin display settings"""

		return self._act_toggle_appearance_options
	
	def showBinSiftSettings(self) -> QtGui.QAction:
		"""Show bin sift settings"""

		return self._act_toggle_sift_settings
	
	def showUserFolder(self) -> QtGui.QAction:
		"""Open the user data folder"""

		return self._act_show_local_storage
	
	def showLogViewer(self) -> QtGui.QAction:
		"""Show the log viewer window"""

		return self._act_show_log_viewer
	
	def checkForUpdates(self) -> QtGui.QAction:
		"""Check for updates"""

		return self._act_check_updates
	
	def visitDiscussionBoard(self) -> QtGui.QAction:
		"""Visit the discussion boards"""

		return self._act_open_discussions
	
	def toggleBinView(self) -> QtGui.QAction:
		"""Toggle filtering columns through the bin view"""

		return self._act_toggle_use_binview
	
	def toggleBinItemFilters(self) -> QtGui.QAction:
		"""Toggle filtering of bin items"""

		return self._act_toggle_use_binfilters
	
	def toggleBinAppearance(self) -> QtGui.QAction:
		"""Toggle saved fonts and colors"""

		return self._act_toggle_use_binappearance
	
	def toggleBinSettingsActionGroup(self) -> QtGui.QActionGroup:
		"""Toggles for saved bin settings"""

		return self._actgrp_toggle_binsettings