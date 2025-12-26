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
		self._item_margins = QtCore.QMarginsF(*[0.1]*4)
		self._thumb_size   = QtCore.QSizeF(16,9)

		self._label_margins = QtCore.QMarginsF(*[0.8]*4)

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
			QtCore.QPointF(thumb_rect.left(), thumb_rect.bottom()),
			QtCore.QPointF(thumb_rect.right(), active_rect.bottom())
		).marginsRemoved(self._label_margins)

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
		painter.restore()

	def _draw_base(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, widget:QtWidgets.QWidget):
		
		painter.setPen(self._brushes.pen_base)
		painter.setBrush(self._brushes.brush_base)
		painter.drawRect(self.activeRect())

	def _draw_thumb(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, widget:QtWidgets.QWidget):

		painter.setPen(self._brushes.pen_none)
		painter.setBrush(self._brushes.brush_thumb)
		painter.drawRect(self.thumbRect())

	def _draw_label(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, widget:QtWidgets.QWidget):
		
		font_name = QtGui.QFont(self._brushes.font_label)
		font_name.setBold(True)

		font_type = QtGui.QFont(self._brushes.font_label)
		
		
		text_line_height = QtCore.QPointF(0, self._brushes.font_metrics.lineSpacing())
		line_2_rect = self.labelRect().translated(text_line_height)

		text_formatted = self._brushes.font_metrics.elidedText(self._name, QtGui.Qt.TextElideMode.ElideMiddle, self.labelRect().width())
		
		painter.setPen(self._brushes.pen_selected) if self.isSelected() else painter.setPen(self._brushes.pen_label)	
		painter.setFont(font_name)
		painter.drawText(self.labelRect(),  text_formatted, o=self._brushes.options_label)
		
		painter.setFont(font_type)
		painter.drawText(line_2_rect, str(self._clip_type), o=self._brushes.options_label)

	def _draw_selection(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, widget:QtWidgets.QWidget):

		painter.setPen(self._brushes.pen_selected)
		painter.setBrush(self._brushes.brush_selected)
		painter.drawRect(self.activeRect())

	def _draw_clip_color(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, widget:QtWidgets.QWidget):
		
		pen = self._brushes.pen_clip_color
		pen.setColor(self._clip_color)
		painter.setPen(pen)
		painter.setBrush(self._brushes.brush_none)

		rect_clip_color = self.thumbRect().marginsRemoved(QtCore.QMarginsF(*[0.1]*4))
		
		painter.drawRect(rect_clip_color)

	@QtCore.Slot(str)
	def setName(self, name:str):

		if self._name == name:
			return
		
		self._name = name
		self.setToolTip(self._name)
		self.update(self.labelRect())

	@QtCore.Slot(QtGui.QColor)
	def setClipColor(self, clip_color:QtGui.QColor):

		clip_color = QtGui.QColor(clip_color)

		if self._clip_color == clip_color:
			return
		
		self._clip_color = clip_color

	def clipType(self) -> avbutils.bins.BinDisplayItemTypes:

		return self._clip_type
	
	@QtCore.Slot(object)
	def setClipType(self, clip_type:avbutils.bins.BinDisplayItemTypes):

		if self._clip_type == clip_type:
			return
		
		self._clip_type = clip_type
		self.update(self.labelRect())