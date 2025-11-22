from PySide6 import QtCore, QtGui, QtWidgets

class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	sig_scale_changed = QtCore.Signal(int)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

		self._current_zoom = 1
	
	def drawBackground(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		raise DeprecationWarning("WHAT")
		
		BASE_MAGNIFICATION = 12
		
		GRID_WIDTH         = 16 * BASE_MAGNIFICATION
		GRID_HEIGHT        =  9 * BASE_MAGNIFICATION
		GRID_DIVISIONS     =  3

		super().drawBackground(painter, rect)

		painter.save()

		for x in range(int(rect.left()), int(rect.right())+1):

			if x%GRID_WIDTH == 0:

				painter.drawLine(QtCore.QLine(
					QtCore.QPoint(x, rect.top()),
					QtCore.QPoint(x, rect.bottom())
				))

				print("HEY YOOHO HO")
				#painter.drawText(QtCore.QPoint(x, 50), f"{x},0")


		for y in range(int(rect.top()), int(rect.bottom())+1):

			if y%GRID_HEIGHT == 0:

				painter.drawLine(QtCore.QLine(
					QtCore.QPoint(rect.left(),  y),
					QtCore.QPoint(rect.right(), y)
				))

		painter.restore()

		self.setZoom(4)

	@QtCore.Slot(int)
	def setZoom(self, zoom_level:int):
		#print("I SET ZOOM", zoom_level)

		if zoom_level != self._current_zoom:
			
			import logging
			logging.getLogger(__name__).debug("Setting zoom level to %s", zoom_level)

			zoom_level = float(zoom_level) #/ float(4)
			self._current_zoom = zoom_level

			t = QtGui.QTransform()
			t.scale(zoom_level, zoom_level)
			self.setTransform(t)

			self.sig_scale_changed.emit(zoom_level)
	
	def drawBackground(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		GRID_DIVISIONS = 3
		GRID_UNIT_SIZE = QtCore.QSizeF(18,12)

		pen_boundary = QtGui.QPen()
		pen_boundary.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen_boundary.setCosmetic(True)
		pen_boundary.setWidth(1)
		pen_boundary.setColor(self.parentWidget().palette().shadow().color())

		pen_division = QtGui.QPen()
		pen_division.setStyle(QtCore.Qt.PenStyle.DashLine)
		pen_division.setCosmetic(True)
		pen_division.setWidth(1)
		pen_division.setColor(self.parentWidget().palette().shadow().color())

		super().drawBackground(painter, rect)

		painter.save()

		# Setup stuff for ruler
		
		coord_font = self.font()
		coord_font.setPointSizeF(coord_font.pointSizeF()/(self._current_zoom))
		painter.setFont(coord_font)
		
		#import logging
		#logging.getLogger(__name__).debug("Set font size to %s px", coord_font.pointSizeF())

		mapped_viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()

		y_top = mapped_viewport_rect.top()
		x_left = mapped_viewport_rect.left()

		for x in range(round(rect.left()), round(rect.right())+1):

			if x % (GRID_UNIT_SIZE.width() // GRID_DIVISIONS):
				continue

			if x % (GRID_UNIT_SIZE.width()) == 0:
				painter.setPen(pen_boundary)
			else:
				painter.setPen(pen_division)
			
			painter.drawLine(QtCore.QLine(
				QtCore.QPoint(x, rect.top()),
				QtCore.QPoint(x, rect.bottom())
			))

			painter.drawText(QtCore.QPointF(x, float(y_top) - (float(y_top) - float(y_top + GRID_UNIT_SIZE.height()))-11), str(int(x)))
		
		for y in range(int(rect.top()), int(rect.bottom())+1):
			
			if y % (GRID_UNIT_SIZE.height() // GRID_DIVISIONS):
				continue

			if y % (GRID_UNIT_SIZE.height()) == 0:
				painter.setPen(pen_boundary)
			else:
				painter.setPen(pen_division)
			
			painter.drawLine(QtCore.QLine(
				QtCore.QPoint(rect.left(), y),
				QtCore.QPoint(rect.right(), y),
			))

			painter.drawText(QtCore.QPoint(float(x_left) - (float(x_left) - float(x_left + GRID_UNIT_SIZE.width())+18), y), str(int(y)))

		painter.restore()