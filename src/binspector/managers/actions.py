"""
Actions
"""

from PySide6 import QtGui, QtWidgets

class ActionsManager:
	"""Actions?"""

	def __init__(self, parent:QtWidgets.QWidget):

		self._parent = parent

		# File actions
		self._act_filebrowser = QtGui.QAction("Open Bin...", self._parent)
		self._act_filebrowser.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
		self._act_filebrowser.setToolTip("Choose a bin to open")
		self._act_filebrowser.setShortcut(QtGui.QKeySequence.StandardKey.Open)

		# Window actions
		self._act_newwindow = QtGui.QAction("New Window...", self._parent)
		self._act_newwindow.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowNew))
		self._act_newwindow.setToolTip("Open a new window")
		self._act_newwindow.setShortcut(QtGui.QKeySequence.StandardKey.New)

		self._act_closewindow = QtGui.QAction("Close Window", self._parent)
		self._act_closewindow.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowClose))
		self._act_closewindow.setToolTip("Close this window")
		self._act_closewindow.setShortcut(QtGui.QKeySequence.StandardKey.Close)

		# Application actions
		self._act_quitapplication = QtGui.QAction("&Quit", self._parent)
		self._act_quitapplication.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ApplicationExit))
		self._act_quitapplication.setToolTip(f"Quit {QtWidgets.QApplication.instance().applicationName()}")
		self._act_quitapplication.setShortcut(QtGui.QKeySequence.StandardKey.Quit)
		self._act_quitapplication.setMenuRole(QtGui.QAction.MenuRole.QuitRole)

		# View modes
		self._act_view_list   = QtGui.QAction("List View", checkable=True, checked=True, parent=self._parent)
		self._act_view_list.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FormatJustifyFill))
		self._act_view_list.setToolTip("Show items in list view mode")

		self._act_view_frame  = QtGui.QAction("Frame View", checkable=True, parent=self._parent)
		self._act_view_frame.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AudioCard))
		self._act_view_frame.setToolTip("Show items in frame view mode")

		self._act_view_script = QtGui.QAction("Script View", checkable=True, parent=self._parent)
		self._act_view_script.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._act_view_script.setToolTip("Show items in script view mode")

		# Bin settings
		self._act_toggle_bindisplay_settings  = QtGui.QAction("Show Bin Display Settings", checkable=True, parent=self._parent)
		self._act_toggle_bindisplay_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentPageSetup))

		self._act_toggle_bindview_settings    = QtGui.QAction("Show Bin View Settings", checkable=True, parent=self._parent)
		self._act_toggle_bindview_settings.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRestore))
		
		self._act_toggle_appearance_options = QtGui.QAction("Show Appearance Settings", checkable=True, parent=self._parent)
		self._act_toggle_appearance_options.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.Battery))


		# Action Groups
		self._actgrp_file = QtGui.QActionGroup(self._parent)
		self._actgrp_file.addAction(self._act_filebrowser)
		
		self._actgrp_window = QtGui.QActionGroup(self._parent)
		self._actgrp_file.addAction(self._act_newwindow)
		self._actgrp_file.addAction(self._act_closewindow)

		self._actgrp_app = QtGui.QActionGroup(self._parent)
		self._actgrp_file.addAction(self._act_quitapplication)

		self._actgrp_view_mode = QtGui.QActionGroup(self._parent)
		self._actgrp_view_mode.setExclusive(True)
		self._actgrp_view_mode.addAction(self._act_view_list)
		self._actgrp_view_mode.addAction(self._act_view_frame)
		self._actgrp_view_mode.addAction(self._act_view_script)

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

		return self._act_toggle_bindview_settings
	
	def showBinAppearanceSettings(self) -> QtGui.QAction:
		"""Show bin display settings"""

		return self._act_toggle_appearance_options