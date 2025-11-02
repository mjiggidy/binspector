from PySide6 import QtCore, QtGui

def draw_clip_color_chip(
		painter      :QtGui.QPainter,
		canvas       :QtCore.QRect,
		clip_color   :QtGui.QColor,
		*,
		border_color :QtGui.QColor|None=None,
		border_width :int=2,
		shadow_color :QtGui.QColor|None=None,
		shadow_alpha :float=0.25
	):
	
	border_color = border_color or QtGui.QPalette().buttonText()
	shadow_color = shadow_color or QtGui.QPalette().shadow()
	
	# No border and no clip color?
	if not clip_color.isValid() and (border_width==0 or not border_color.isValid()):
		raise ValueError("Nothing to draw")
	
	# Calculate margins for stroke and shadow
	margins = QtCore.QMargins(*([border_width * 2] * 4))
	active_rect = canvas.marginsRemoved(margins)

	# Pen and brush initial values
	pen = painter.pen()
	pen.setWidth(border_width)
	pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
	
	brush = painter.brush()

	painter.save()
	#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

	# Draw shadow first I guess
	if shadow_color.isValid() and border_width > 0:

		shadow_offset = QtCore.QPoint(border_width,border_width)
		active_rect.translate(shadow_offset)
		
		shadow_color.setAlphaF(shadow_alpha)
		pen.setColor(shadow_color)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		
		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRect(active_rect)

		active_rect.translate(-shadow_offset)

	# Draw main clip color chip
	pen.setColor(border_color)

	brush.setColor(clip_color)
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern if clip_color.isValid() else QtCore.Qt.BrushStyle.NoBrush)

	painter.setPen(pen)
	painter.setBrush(brush)

	painter.drawRect(active_rect)

	painter.restore()