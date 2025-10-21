from PySide6 import QtCore, QtGui, QtWidgets

class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

		self.setZoom(4)

	@QtCore.Slot(int)
	def setZoom(self, zoom_level:int):

		zoom_level = float(zoom_level) #/ float(4)
		
		t = QtGui.QTransform()
		t.scale(zoom_level, zoom_level)
		self.setTransform(t)
	
	def drawBackground(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		GRID_DIVISIONS = 3
		GRID_UNIT_RECT = QtCore.QRectF(
			QtCore.QPoint(0,0),
			QtCore.QPoint(18,12)
		)

		pen_boundary = QtGui.QPen()
		pen_boundary.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen_boundary.setCosmetic(True)
		pen_boundary.setWidth(1)

		pen_division = QtGui.QPen()
		pen_division.setStyle(QtCore.Qt.PenStyle.DashLine)
		pen_division.setCosmetic(True)
		pen_division.setWidth(1)

		
		super().drawBackground(painter, rect)

		painter.save()

		for x in range(round(rect.left()), round(rect.right())+1):

			if x % (GRID_UNIT_RECT.width() // GRID_DIVISIONS):
				continue

			if x % (GRID_UNIT_RECT.width()) == 0:
				painter.setPen(pen_boundary)
			else:
				painter.setPen(pen_division)
			
			painter.drawLine(QtCore.QLine(
				QtCore.QPoint(x, rect.top()),
				QtCore.QPoint(x, rect.bottom())
			))
		
		for y in range(int(rect.top()), int(rect.bottom())+1):
			
			if y % (GRID_UNIT_RECT.height() // GRID_DIVISIONS):
				continue

			if y % (GRID_UNIT_RECT.height()) == 0:
				painter.setPen(pen_boundary)
			else:
				painter.setPen(pen_division)
			
			painter.drawLine(QtCore.QLine(
				QtCore.QPoint(rect.left(), y),
				QtCore.QPoint(rect.right(), y),
			))


		painter.restore()