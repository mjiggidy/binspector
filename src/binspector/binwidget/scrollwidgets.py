"""
Widgets for adding as scrollBarWidgets to `QScrollArea`

Mostly standard widgets sublcassed for style
"""

from PySide6 import QtCore, QtWidgets

class BSBinStatsLabel(QtWidgets.QLabel):
	"""Display label intended for use in a `QScrollArea` widget"""

	def __init__(
		self,
		*args,
		font_scale:float=0.8,
		char_width:int=32,  # len("Showing 999,999 of 999,999 items")
		**kwargs
	):

		super().__init__(*args, **kwargs)

		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, self.sizePolicy().verticalPolicy())
		self.setAlignment (QtCore.Qt.AlignmentFlag.AlignCenter)
		self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel|QtWidgets.QFrame.Shadow.Sunken)

		f = self.font()
		f.setPointSizeF(f.pointSizeF() * font_scale)
		self.setFont(f)
		
		self.setMinimumWidth(self.fontMetrics().averageCharWidth() * char_width)