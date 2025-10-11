from PySide6 import QtCore, QtGui

def draw_clip_color_chip(
		painter:QtGui.QPainter,
		canvas:QtCore.QRect,
		clip_color:QtGui.QColor,
		*,
		border_color:QtGui.QColor,
		border_width:int,
		shadow_color:QtGui.QColor
		):
	
	# No border and no clip color?
	if not clip_color.isValid() and (border_width==0 or not border_color.isValid()):
		raise ValueError("Nothing to draw")
	
	painter.save()

	# Draw clip color chip
	pen = painter.pen()
	pen.setColor(border_color)
	pen.setWidth(border_width)
	painter.setPen(pen)

	brush = painter.brush()
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern if clip_color.isValid() else QtCore.Qt.BrushStyle.NoBrush)
	brush.setColor(clip_color)
	painter.setBrush(brush)

	painter.drawRect(canvas)

	# Draw shadow if set
	if not shadow_color.isValid() or border_width==0:
		painter.restore()
		return
	shadow_color.setAlphaF(0.25)
	
	canvas.translate(border_width,border_width)
	
	pen = painter.pen()
	pen.setColor(shadow_color)
	pen.setWidth(border_width)
	painter.setPen(pen)

	painter.setBrush(QtGui.QBrush(QtCore.Qt.BrushStyle.NoBrush))

	painter.drawRect(canvas)

	painter.restore()