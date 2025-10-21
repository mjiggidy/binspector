from PySide6 import QtCore, QtGui, QtWidgets

class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

	@QtCore.Slot(int)
	def setZoom(self, zoom_level:int):

		zoom_level = float(zoom_level) / float(4)
		
		t = QtGui.QTransform()
		t.scale(zoom_level, zoom_level)
		self.setTransform(t)