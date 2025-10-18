from PySide6 import QtCore, QtGui, QtWidgets

class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setScene(QtWidgets.QGraphicsScene())

		self.scene().addText("Look At This Frame View Haha Wow")