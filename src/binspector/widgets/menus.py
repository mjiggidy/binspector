"""
Menus used by things that use menus
"""

from PySide6 import QtGui, QtWidgets
from ..core import actions

class BinWindowMenuBar(QtWidgets.QMenuBar):

	def __init__(self, action_manager:actions.ActionsManager, *args, **kwargs):
		
		super()	.__init__(*args, **kwargs)

		mnu_main = QtWidgets.QMenu("&File")
		mnu_view = QtWidgets.QMenu("&View")
		mnu_window = QtWidgets.QMenu("&Window")
		

		mnu_main.addAction(action_manager.newWindowAction())
		mnu_main.addAction(action_manager.fileBrowserAction())
		mnu_main.addSeparator()
		mnu_main.addAction(action_manager.quitApplicationAction())

		mnu_view.addAction(action_manager.viewBinAsList())
		mnu_view.addAction(action_manager.viewBinAsFrame())
		mnu_view.addAction(action_manager.viewBinAsScript())
		mnu_view.addSeparator()
		mnu_view.addAction(action_manager.showBinDisplaySettings())
		mnu_view.addAction(action_manager.showBinViewSettings())
		mnu_view.addAction(action_manager.showBinAppearanceSettings())
		mnu_view.addSeparator()

		mnu_window.addAction(action_manager.closeWindowAction())

		self.addMenu(mnu_main)
		self.addMenu(mnu_view)
		self.addMenu(mnu_window)