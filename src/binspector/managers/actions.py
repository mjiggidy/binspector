"""
Actions
"""

from PySide6 import QtCore, QtGui, QtWidgets

class ActionsManager(QtCore.QObject):
	"""General actions"""

	def __init__(self, parent:QtWidgets.QWidget|None=None):


		self._parent = parent or self
		super().__init__(parent=parent)

		# File actions
		self._act_filebrowser = QtGui.QAction("&Open Bin...")
		"""Request file browser to choose new bin"""
		self._act_filebrowser.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
		self._act_filebrowser.setToolTip("Choose a bin to open")
		self._act_filebrowser.setShortcut(QtGui.QKeySequence.StandardKey.Open)

		self._act_reloadcurrent = QtGui.QAction("&Reload Current Bin")
		self._act_reloadcurrent.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		self._act_reloadcurrent.setToolTip("Reload the current bin")
		self._act_reloadcurrent.setShortcut(QtGui.QKeySequence.StandardKey.Refresh)

		self._act_stopcurrent = QtGui.QAction("Stop Loading")
		self._act_stopcurrent.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ProcessStop))
		self._act_stopcurrent.setToolTip("Stop loading the current bin")
		self._act_stopcurrent.setShortcut(QtGui.QKeySequence.StandardKey.Cancel)

		# Window actions
		self._act_newwindow = QtGui.QAction("&New Window...")
		"""Request new bin window"""
		self._act_newwindow.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowNew))
		self._act_newwindow.setToolTip("Open a new window")
		self._act_newwindow.setShortcut(QtGui.QKeySequence.StandardKey.New)
		#self._act_newwindow.setShortcutContext(QtGui.Qt.ShortcutContext.ApplicationShortcut)

		self._act_closewindow = QtGui.QAction("Close &Window")
		"""Close active bin window"""
		self._act_closewindow.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowClose))
		self._act_closewindow.setToolTip("Close this window")
		self._act_closewindow.setShortcut(QtGui.QKeySequence.StandardKey.Close)

		# Application actions
		self._act_quitapplication = QtGui.QAction("&Quit")
		"""Quit application"""
		self._act_quitapplication.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ApplicationExit))
		self._act_quitapplication.setToolTip(f"Quit {QtWidgets.QApplication.instance().applicationName()}")
		self._act_quitapplication.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
		self._act_quitapplication.setMenuRole(QtGui.QAction.MenuRole.QuitRole)
		#self._act_quitapplication.setShortcutContext(QtGui.Qt.ShortcutContext.ApplicationShortcut)

		# View modes
		self._act_view_list   = QtGui.QAction("List View", checkable=True, checked=True, parent=self._parent)
		"""Toggle Bin View Mode: List"""
		self._act_view_list.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FormatJustifyFill))
		self._act_view_list.setShortcut(QtGui.QKeySequence(QtGui.Qt.Modifier.CTRL|QtGui.Qt.Key.Key_1))
		self._act_view_list.setToolTip("Show items in list view mode")

		self._act_view_frame  = QtGui.QAction("Frame View", checkable=True, parent=self._parent)
		"""Toggle Bin View Mode: Frame"""
		self._act_view_frame.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AudioCard))
		self._act_view_frame.setShortcut(QtGui.QKeySequence(QtGui.Qt.Modifier.CTRL|QtGui.Qt.Key.Key_2))
		self._act_view_frame.setToolTip("Show items in frame view mode")

		self._act_view_script = QtGui.QAction("Script View", checkable=True, parent=self._parent)
		"""Toggle Bin View Mode: Script"""
		self._act_view_script.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._act_view_script.setShortcut(QtGui.QKeySequence(QtGui.Qt.Modifier.CTRL|QtGui.Qt.Key.Key_3))
		self._act_view_script.setToolTip("Show items in script view mode")

		# Bin settings
		self._act_toggle_bindisplay_settings  = QtGui.QAction("Show Bin Display Settings", checkable=True, parent=self._parent)
		"""Toggle visibility of Bin Display Settings toolbox"""
		self._act_toggle_bindisplay_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentPageSetup))

		self._act_toggle_binview_settings    = QtGui.QAction("Show Bin View Settings", checkable=True, parent=self._parent)
		"""Toggle visibility of Binview Settings toolbox"""
		self._act_toggle_binview_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRestore))
		
		self._act_toggle_appearance_options = QtGui.QAction("Show Appearance Settings", checkable=True, parent=self._parent)
		"""Toggle visibility of Fonts & Colors toolbox"""
		self._act_toggle_appearance_options.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.Battery))

		self._act_toggle_sift_settings = QtGui.QAction("Show Sift Settings", checkable=True, parent=self._parent)
		"""Toggle visibility of Sift Settings toolbox"""
		self._act_toggle_sift_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AudioVolumeHigh))

		# Tools
		self._act_show_local_storage = QtGui.QAction("Open User Data Folder", parent=self._parent)
		"""Open local storage"""
		self._act_show_local_storage.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen))

		self._act_show_log_viewer = QtGui.QAction("Show Log Viewer", parent=self._parent)
		"""Show the log viewer window"""
		self._act_show_log_viewer.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
		self._act_show_log_viewer.setToolTip("Show the log viewer window")
		self._act_show_log_viewer.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.Key.Key_L))





		# Help menu stuff
		self._act_open_discussions = QtGui.QAction("Visit Discussion Board...", parent=self._parent)
		self._act_open_discussions.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DialogInformation))

		self._act_check_updates = QtGui.QAction("Check For Updates...", parent=self._parent)
		self._act_check_updates.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SoftwareUpdateAvailable))
		self._act_check_updates.setMenuRole(QtGui.QAction.MenuRole.ApplicationSpecificRole)

		self._act_show_about = QtGui.QAction(f"About {QtWidgets.QApplication.instance().applicationDisplayName()}...", parent=self._parent)
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