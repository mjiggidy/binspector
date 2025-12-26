from PySide6 import QtCore, QtGui

def draw_marker_tick(
	painter      :QtGui.QPainter,
	canvas       :QtCore.QRect,
	marker_color :QtGui.QColor,
	*,
	border_color :QtGui.QColor|None=None,
	border_width :int=2,
	border_radius:int=4,
	shadow_color :QtGui.QColor|None=None,
	shadow_alpha :float=0.25
):
	border_color = border_color or QtGui.QPalette().buttonText().color()
	shadow_color = shadow_color or QtGui.QPalette().shadow().color()
	
	painter.save()
	painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
	
	active_rect = canvas

	pen = QtGui.QPen()
	pen.setColor(border_color)
	pen.setWidth(border_width)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

	brush = QtGui.QBrush()
	brush.setColor(marker_color)
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern if marker_color.isValid() else QtCore.Qt.BrushStyle.LinearGradientPattern)
	
	# No Marker color?
	if not marker_color:
		raise ValueError("Nothing to draw")
	
	# Draw shadow first I guess
	if shadow_color.isValid() and border_width > 0:

		shadow_offset = QtCore.QPoint(border_width/2,border_width/2)
		active_rect.translate(shadow_offset)
		
		shadow_color.setAlphaF(shadow_alpha)
		pen.setColor(shadow_color)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		
		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRoundedRect(active_rect, border_radius, border_radius)

		active_rect.translate(-shadow_offset)

	brush.setColor(marker_color)
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern if marker_color.isValid() else QtCore.Qt.BrushStyle.LinearGradientPattern)

	pen.setColor(border_color)
	pen.setWidth(border_width)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)	

	painter.setPen(pen)
	painter.setBrush(brush)
	
	painter.drawRoundedRect(
		active_rect, border_radius, border_radius
	)
	
	painter.restore()

def draw_clip_color_chip(
	painter      :QtGui.QPainter,
	canvas       :QtCore.QRectF,
	clip_color   :QtGui.QColor,
	*,
	border_color :QtGui.QColor|None=None,
	border_width :float=2,
	shadow_color :QtGui.QColor|None=None,
	shadow_alpha :float=0.25
):
	
	border_color = border_color or QtGui.QGuiApplication().palette().buttonText().color()
	shadow_color = shadow_color or QtGui.QGuiApplication().palette().shadow().color()
	
	# No border and no clip color?
	if not clip_color.isValid() and (border_width==0 or not border_color.isValid()):
		raise ValueError("Nothing to draw")
	
	# Calculate margins for stroke and shadow
	margins = QtCore.QMarginsF(*([border_width * 2] * 4))
	active_rect = QtCore.QRectF(canvas).marginsRemoved(margins)

	# Pen and brush initial values
	pen = painter.pen()
	pen.setWidth(border_width)
	pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
	
	brush = painter.brush()

	painter.save()
	#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

	# Draw shadow first I guess
	if shadow_color.isValid() and border_width > 0:

		shadow_offset = QtCore.QPointF(border_width,border_width)
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
	brush.setStyle(
		QtCore.Qt.BrushStyle.SolidPattern if clip_color.isValid()
		else QtCore.Qt.BrushStyle.NoBrush
	)

	painter.setPen(pen)
	painter.setBrush(brush)

	painter.drawRect(active_rect)

	painter.restore()