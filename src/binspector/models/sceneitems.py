from PySide6 import QtCore, QtGui, QtWidgets

class BSFrameModeItem(QtWidgets.QGraphicsItem):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._clip_color = QtGui.QColor()

	def boundingRect(self) -> QtCore.QRectF:
		return QtCore.QRectF(QtCore.QPoint(0,0),QtCore.QSize(18,12))
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, /,	 widget:QtWidgets.QWidget = ...):

		painter.save()

		pen = QtGui.QPen()
		pen.setWidth(4)
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
		pen.setCosmetic(True)

		brush = QtGui.QBrush()
		brush.setColor(option.palette.color(QtGui.QPalette.ColorRole.Dark))
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(self.boundingRect())

		brush = QtGui.QBrush()
		brush.setColor(option.palette.color(QtGui.QPalette.ColorRole.Button))
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		pen = QtGui.QPen()
		pen.setStyle(QtCore.Qt.PenStyle.NoPen)
		

		painter.setBrush(brush)
		painter.setPen(pen)

		clip_preview_rect = self.boundingRect().adjusted(0, 0, 0, -1).adjusted(.5,.5,-.5,-.5)

		painter.drawRect(clip_preview_rect)

		if self._clip_color.isValid():
			#pass

			pen = QtGui.QPen()
			pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
			pen.setWidthF(0.25/self.scale())
			pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
			pen.setColor(self._clip_color)
			
			brush = QtGui.QBrush()
			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)

			painter.setPen(pen)
			painter.setBrush(brush)
			painter.drawRect(self.boundingRect().adjusted(.25,.25,-.25,-.25))

		font = QtWidgets.QApplication.font()
		font.setPixelSize(1/self.scale())
		
		painter.setFont(font)
		pen = QtGui.QPen()
		painter.setPen(pen)
		painter.drawText(self.boundingRect().adjusted(0.25,0.25,-0.25,-0.25), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignBottom, self._name)

		painter.drawText(QtCore.QPoint(0,0) + QtCore.QPoint(0,1), f"({self.pos().x():.1f},{self.pos().y():.1f})")
		
		if self.isSelected():
			brush = QtGui.QBrush()
			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
			color_highlight:QtGui.QColor = option.palette.color(QtGui.QPalette.ColorRole.Highlight)
			color_highlight.setAlphaF(0.5)
			brush.setColor(color_highlight)

			pen = QtGui.QPen()
			pen.setStyle(QtCore.Qt.PenStyle.NoPen)

			painter.setBrush(brush)
			painter.setPen(pen)
			painter.drawRect(self.boundingRect())

		
		painter.restore()

	def setName(self, name:str):
		self._name = name
	
	def setClipColor(self, color:QtGui.QColor):

		self._clip_color = color