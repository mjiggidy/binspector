from PySide6 import QtCore, QtGui, QtWidgets
import avbutils
from ..core.config import BSFrameViewConfig
from . import painters

class BSFrameModeItem(QtWidgets.QGraphicsItem):

	def __init__(self, *args, brush_manager:painters.BSFrameItemBrushManager,**kwargs):

		super().__init__(*args, **kwargs)

		self._name         = str()
		self._clip_color   = QtGui.QColor()
		self._clip_type    = avbutils.bins.BinDisplayItemTypes(0)
		
		self._item_size    = BSFrameViewConfig.GRID_UNIT_SIZE
		self._item_margins = QtCore.QMarginsF(*[0.5]*4)
		self._thumb_size   = QtCore.QSizeF(16,9)

		self._brushes      = brush_manager
		
	def brushManager(self) -> painters.BSFrameItemBrushManager:
		return self._brushes
	
	def setBrushManager(self, brush_manager:painters.BSFrameItemBrushManager):
		self._brushes = brush_manager

	def setItemSize(self, item_size:QtCore.QSizeF):
		"""Set the item size.  Recommend: one grid unit"""

		if self._item_size == item_size:
			return

		self._item_size = item_size
		self.update(self.boundingRect())

	def itemSize(self) -> QtCore.QSizeF:
		"""Overall size of the item, including margins and padding. Should be one grid unit."""

		return self._item_size
	
	def setThumbSize(self, thumb_size:QtCore.QSizeF):
		"""Set the thumbnail aspect ratio"""

		if self._thumb_size == thumb_size:
			return

		self._thumb_size = thumb_size
		self.update(self.boundingRect())

	def thumbSize(self) -> QtCore.QSizeF:
		"""Frame thumbnail aspect ratio"""
		
		return self._thumb_size
	
	def thumbRect(self) -> QtCore.QRectF:

		active_rect = self.activeRect()

		thumb_rect = QtCore.QRectF(
			active_rect.topLeft(),
			QtCore.QSizeF(
				active_rect.width(),
				active_rect.width() * (self._thumb_size.height()/self._thumb_size.width())
			)
		).marginsRemoved(self._item_margins/2)

		return thumb_rect
	
	def labelRect(self) -> QtCore.QRectF:
		"""The label area rect"""

		active_rect = self.activeRect()
		thumb_rect  = self.thumbRect()

		return QtCore.QRectF(
			QtCore.QPointF(thumb_rect.left(), thumb_rect.bottom() + self._item_margins.top()),
			QtCore.QPointF(thumb_rect.right(), active_rect.bottom() - self._item_margins.bottom())
		)

	def boundingRect(self) -> QtCore.QRectF:
		"""The overall rect of the item, including margins and padding.  Should be one grid unit."""

		return QtCore.QRectF(QtCore.QPoint(0,0), self._item_size)
	
	def activeRect(self) -> QtCore.QRectF:
		"""The active area with margins and padding calculated.  Should be one grid unit minus padidng."""

		return self.boundingRect().marginsRemoved(self._item_margins)

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, *args,  widget:QtWidgets.QWidget = ...):

		painter.save()

		self._draw_base(painter, option, widget)
		self._draw_thumb(painter, option, widget)
		
		if self._clip_color.isValid():
			self._draw_clip_color(painter, option, widget)

		if self.isSelected():
			self._draw_selection(painter, option, widget)

		self._draw_label(painter, option, widget)


#		pen = QtGui.QPen()
#		pen.setWidth(4)
#		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
#		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
#		pen.setCosmetic(True)
#
#		brush = QtGui.QBrush()
#		brush.setColor(option.palette.color(QtGui.QPalette.ColorRole.Dark))
#		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
#
#		painter.setPen(pen)
#		painter.setBrush(brush)
#		painter.drawRect(self.boundingRect())
#
#		brush = QtGui.QBrush()
#		brush.setColor(option.palette.color(QtGui.QPalette.ColorRole.Button))
#		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
#		pen = QtGui.QPen()
#		pen.setStyle(QtCore.Qt.PenStyle.NoPen)
#
#
#		painter.setBrush(brush)
#		painter.setPen(pen)
#
#		clip_preview_rect = self.boundingRect().adjusted(0, 0, 0, -1).adjusted(.5,.5,-.5,-.5)
#
#		painter.drawRect(clip_preview_rect)
#
#		if self._clip_color.isValid():
#			#pass
#
#			pen = QtGui.QPen()
#			pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
#			pen.setWidthF(0.25/self.scale())
#			pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
#			pen.setColor(self._clip_color)
#
#			brush = QtGui.QBrush()
#			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
#
#			painter.setPen(pen)
#			painter.setBrush(brush)
#			painter.drawRect(self.boundingRect().adjusted(.25,.25,-.25,-.25))
#
#		font = QtWidgets.QApplication.font()
#		font.setPixelSize(1/self.scale())
#
#		painter.setFont(font)
#		pen = QtGui.QPen()
#		painter.setPen(pen)
#		painter.drawText(self.boundingRect().adjusted(0.25,0.25,-0.25,-0.25), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignBottom, self._name)
#
#		painter.drawText(QtCore.QPoint(0,0) + QtCore.QPoint(0,1), f"({self.pos().x():.1f},{self.pos().y():.1f})")
#
#		if self.isSelected():
#			brush = QtGui.QBrush()
#			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
#			color_highlight:QtGui.QColor = option.palette.color(QtGui.QPalette.ColorRole.Highlight)
#			color_highlight.setAlphaF(0.5)
#			brush.setColor(color_highlight)
#
#			pen = QtGui.QPen()
#			pen.setStyle(QtCore.Qt.PenStyle.NoPen)
#
#			painter.setBrush(brush)
#			painter.setPen(pen)
#			painter.drawRect(self.boundingRect())
#
#
		painter.restore()

	def _draw_base(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, *args,  widget:QtWidgets.QWidget = ...):
		
		painter.setPen(self._brushes.pen_base)
		painter.setBrush(self._brushes.brush_base)
		painter.drawRect(self.activeRect())

	def _draw_thumb(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, *args,  widget:QtWidgets.QWidget = ...):

		painter.setPen(self._brushes.pen_none)
		painter.setBrush(self._brushes.brush_thumb)
		painter.drawRect(self.thumbRect())

	def _draw_label(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, *args,  widget:QtWidgets.QWidget = ...):
		
		painter.setFont(self._brushes.font_label)
		painter.setPen(self._brushes.pen_selected) if self.isSelected() else painter.setPen(self._brushes.pen_label)	
		painter.drawText(self.labelRect(), self._name + "\n" + str(self._clip_type), o=QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignLeft)

	def _draw_selection(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, *args,  widget:QtWidgets.QWidget = ...):

		painter.setPen(self._brushes.pen_selected)
		painter.setBrush(self._brushes.brush_selected)
		painter.drawRect(self.activeRect())

	def _draw_clip_color(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, *args,  widget:QtWidgets.QWidget = ...):
		
		pen = self._brushes.pen_clip_color
		pen.setColor(self._clip_color)
		painter.setPen(pen)
		painter.setBrush(self._brushes.brush_none)

		rect_clip_color = self.thumbRect()#.marginsRemoved(QtCore.QMarginsF(*[.05]*4))
		
		painter.setPen(self._brushes.pen_base)
		
		painter.drawRect(rect_clip_color)

	@QtCore.Slot(str)
	def setName(self, name:str):

		if self._name == name:
			return
		
		self._name = name
		self.update(self.labelRect())

	@QtCore.Slot(QtGui.QColor)
	def setClipColor(self, clip_color:QtGui.QColor):

		#print("!!!!!!! COLOR NOT SET TO", clip_color)
		clip_color = QtGui.QColor(clip_color)

		if self._clip_color == clip_color:
			return
		
		self._clip_color = clip_color
		#print("****** COLOR SET TO", self._clip_color)
		#self.update(self.boundingRect())

	def clipType(self) -> avbutils.bins.BinDisplayItemTypes:

		return self._clip_type
	
	@QtCore.Slot(object)
	def setClipType(self, clip_type:avbutils.bins.BinDisplayItemTypes):

		#print("^^^^^^ SETTING TYPE TO ", clip_type)

		if self._clip_type == clip_type:
			return
		
		self._clip_type = clip_type
		self.update(self.labelRect())