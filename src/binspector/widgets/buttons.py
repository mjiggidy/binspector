from PySide6 import QtCore, QtGui, QtWidgets

class LBPushButtonAction(QtWidgets.QPushButton):
	"""A QPushButton bound to a QAction"""

	def __init__(self, action:QtGui.QAction|None=None, show_text:bool=True, show_icon:bool=True, show_tooltip:bool=True, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._action = None
		
		self._show_text    = show_text
		self._show_icon    = show_icon
		self._show_tooltip = show_tooltip

		if action:
			self.setAction(action)
	
	def setAction(self, action:QtGui.QAction):
		"""Set the action this button will be bound to"""

		# Disconnect previous action
		if self._action:

			self._action.enabledChanged.disconnect(self.setEnabled)
			self._action.visibleChanged.disconnect(self.setVisible)
			self._action.checkableChanged.disconnect(self.setCheckable)
			self._action.toggled.disconnect(self.setChecked)

			self.clicked.disconnect(self._action.trigger)
		
		# Set new action
		self._action = action

		# Sync current state with new action
		self.setEnabled(self._action.isEnabled())
		self.setVisible(self._action.isVisible())
		self.setCheckable(self._action.isCheckable())
		self.setChecked(self._action.isChecked())
		self.setIcon(self._action.icon() if self._show_icon else QtGui.QIcon())
		self.setToolTip(self._action.toolTip() if self._show_tooltip else None)
		self.setText(self._action.text() if self._show_text else None)

		# Sync future state changes
		self._action.enabledChanged.connect(self.setEnabled)
		self._action.visibleChanged.connect(self.setVisible)
		self._action.checkableChanged.connect(self.setCheckable)
		self._action.toggled.connect(self.setChecked)

		self.clicked.connect(self._action.trigger)