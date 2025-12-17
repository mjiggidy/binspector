import sys
from PySide6 import QtCore, QtGui, QtWidgets

class ColorPaletteLabel(QtWidgets.QLabel):

	def __init__(self, color_role:QtGui.QPalette.ColorRole):

		super().__init__()

		self._color_role = color_role

		self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.setAutoFillBackground(True)

		self.setPalette(self.palette())
	
	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(128,64)/2
	
	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):


		color = self.palette().color(self._color_role)

		palette.setColor(QtGui.QPalette.ColorRole.Window, color)
		palette.setColor(QtGui.QPalette.ColorRole.Base, color)
		palette.setColor(QtGui.QPalette.ColorRole.Accent, color)

		self.setText(color.name())

		return super().setPalette(palette)

class MyKewlPaletteViewer(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())

		for row, color_role in enumerate(QtGui.QPalette.ColorRole):

			self.layout().addWidget(QtWidgets.QLabel(color_role.name), row, 0)
			self.layout().addWidget(ColorPaletteLabel(color_role), row, 1)


if __name__ == "__main__":

	app = QtWidgets.QApplication()

	wnd = MyKewlPaletteViewer()
	wnd.show()

	sys.exit(app.exec())