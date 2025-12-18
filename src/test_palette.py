import sys
from PySide6 import QtCore, QtGui, QtWidgets

ORDERED_COLOR_ROLES = [
	QtGui.QPalette.ColorRole.Base,
	QtGui.QPalette.ColorRole.AlternateBase,
	QtGui.QPalette.ColorRole.Window,
	QtGui.QPalette.ColorRole.ToolTipBase,

	QtGui.QPalette.ColorRole.Text,
	QtGui.QPalette.ColorRole.WindowText,
	QtGui.QPalette.ColorRole.ToolTipText,
	QtGui.QPalette.ColorRole.PlaceholderText,
	QtGui.QPalette.ColorRole.ButtonText,
	QtGui.QPalette.ColorRole.BrightText,

	QtGui.QPalette.ColorRole.Light,
	QtGui.QPalette.ColorRole.Midlight,
	QtGui.QPalette.ColorRole.Button,
	QtGui.QPalette.ColorRole.Mid,
	QtGui.QPalette.ColorRole.Dark,
	QtGui.QPalette.ColorRole.Shadow,

	QtGui.QPalette.ColorRole.Accent,
	QtGui.QPalette.ColorRole.Highlight,
	QtGui.QPalette.ColorRole.HighlightedText,

	QtGui.QPalette.ColorRole.Link,
	QtGui.QPalette.ColorRole.LinkVisited,
]

class ColorPaletteLabel(QtWidgets.QLabel):

	def __init__(self, color_role:QtGui.QPalette.ColorRole, color_group:QtGui.QPalette.ColorGroup=QtGui.QPalette.ColorGroup.Active):

		super().__init__()

		self._color_role  = color_role
		self._color_group = color_group

		self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.setAutoFillBackground(True)

		self._updateColor()
	
	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(128,64) / 2
	
	@QtCore.Slot()
	def _updateColor(self):

		palette = self.palette()
		
		color = self.palette().color(self._color_group, self._color_role)
		palette.setColor(QtGui.QPalette.ColorRole.Window, color)

		print(palette)

		self.setPalette(palette)
		self.setText(f"R: {color.red()}  G: {color.green()}  B: {color.blue()} A: {color.alpha()}")
		self.setToolTip(color.name())
	
	@QtCore.Slot(QtGui.QPalette.ColorRole)
	def setColorRole(self, role:QtGui.QPalette.ColorRole):

		self._color_role = role
		self._updateColor()
	
	@QtCore.Slot(QtGui.QPalette.ColorGroup)
	def setColorGroup(self, group:QtGui.QPalette.ColorGroup):

		self._color_group = group
		self._updateColor()

	def setPalette(self, arg__1):
		super().setPalette(arg__1)
		self._updateColor()

class MyKewlPaletteViewer(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())

		self._cmb_colorgroups = QtWidgets.QComboBox()
		
		for group in QtGui.QPalette.ColorGroup:
			self._cmb_colorgroups.addItem(group.name, group)

		self.layout().addWidget(self._cmb_colorgroups, 0, 0, 1, 2)

		for row, color_role in enumerate(ORDERED_COLOR_ROLES):

			swatch = ColorPaletteLabel(color_role)
			self._cmb_colorgroups.activated.connect(lambda: swatch.setColorGroup(self._cmb_colorgroups.currentData()))

			self.layout().addWidget(QtWidgets.QLabel(color_role.name), row+1, 0)
			self.layout().addWidget(swatch, row+1, 1)
	
if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = MyKewlPaletteViewer()
	wnd.show()

	sys.exit(app.exec())