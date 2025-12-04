from __future__ import annotations
import logging, dataclasses, typing
from PySide6 import QtCore, QtGui, QtWidgets

from ...managers import overlaymanager
from . import abstractoverlay

DEFAULT_RULER_SIZE = 24
DEFAULT_RULER_OUTLINE_WIDTH = 1
DEFAULT_FANCY_ALPHA = 0.75
DEFAULT_FONT_SCALE = 0.7
DEFAULT_RULER_POSITION = QtCore.QPointF(50,30)

@dataclasses.dataclass(frozen=True)
class BSRulerTickInfo:
	"""Ruler tick info"""

	ruler_offset: int|float
	"""Pixel offset from widget rect"""

	tick_label:   str
	"""Label to print"""


class BSFrameRulerOverlay(abstractoverlay.BSAbstractOverlay):

	sig_ruler_size_changed         = QtCore.Signal(int)
	sig_ruler_ticks_changed        = QtCore.Signal(object)
	sig_ruler_orientations_changed = QtCore.Signal(object)
	sig_ruler_position_changed     = QtCore.Signal(object)

	def __init__(self, *args, ruler_size:int=DEFAULT_RULER_SIZE, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._ruler_position = DEFAULT_RULER_POSITION
		
		self._ruler_ticks:dict[QtCore.Qt.Orientation, list[BSRulerTickInfo]] = {
			QtCore.Qt.Orientation.Horizontal: set(),
			QtCore.Qt.Orientation.Vertical:   set(),
		}

		self._ruler_size        = ruler_size
		self._ruler_tick_size   = 4

		self._ruler_orientations= set([
			QtCore.Qt.Orientation.Horizontal,
			QtCore.Qt.Orientation.Vertical
		])

		self._ruler_stroke      = DEFAULT_RULER_OUTLINE_WIDTH

		# Pens
		self._pen_ruler_base    = QtGui.QPen()

		self._pen_ruler_base.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen_ruler_base.setCapStyle(QtCore.Qt.PenCapStyle.SquareCap)
		self._pen_ruler_base.setJoinStyle(QtCore.Qt.PenJoinStyle.BevelJoin)

		self._pen_ruler_ticks   = QtGui.QPen(self._pen_ruler_base)
		self._pen_mouse_coords  = QtGui.QPen(self._pen_ruler_base)

		# Brushes
		self._brush_ruler_base  = QtGui.QLinearGradient()

		# Fonts
		self._font_mouse_coords = QtGui.QFont()
		
		self._font.setPointSizeF(self._font.pointSizeF() * DEFAULT_FONT_SCALE)
		self.setFont(self._font)
	
	@QtCore.Slot(object)
	def setRulerPosition(self, ruler_position:QtCore.QPoint|QtCore.QPointF):

		if self._ruler_position != ruler_position:
			
			self._ruler_position = ruler_position
			self.sig_ruler_position_changed.emit(ruler_position)
			self.sig_update_requested.emit()

	def rulerPosition(self) -> QtCore.QPoint|QtCore.QPointF:

		return self._ruler_position


	@QtCore.Slot(object)
	def setRulerOrientations(self, orientations:typing.Iterable[QtCore.Qt.Orientation]):
		"""Set ruler display orientations"""

		if self._ruler_orientations != orientations:
			
			self._ruler_orientations = orientations
			self.sig_ruler_orientations_changed.emit(orientations)
			self.sig_update_requested.emit()
	
	def rulerOrientations(self) -> set[QtCore.Qt.Orientation]:

		return set(self._ruler_orientations)
	
	@QtCore.Slot(object)
	def setTicks(self, ruler_ticks:typing.Iterable[BSRulerTickInfo], orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal):

		self._ruler_ticks[orientation] = set(ruler_ticks)
		self.sig_ruler_ticks_changed.emit(ruler_ticks)
		self.sig_update_requested.emit()
	
	def ticks(self, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal) -> list[BSRulerTickInfo]:

		return list(self._ruler_orientations[orientation])

	@QtCore.Slot(QtGui.QFont)
	def setFont(self, new_font:QtGui.QFont):

		#new_font.setPointSizeF(new_font.pointSizeF() * 0.8)
		
		super().setFont(new_font)
		self.setupDrawingTools()
		self.sig_update_requested.emit()

	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, new_palette:QtGui.QPalette):

		super().setPalette(new_palette)
		self.setupDrawingTools()
		self.sig_update_requested.emit()

	@QtCore.Slot()
	def setupDrawingTools(self):
		"""Setup pens, brushes and fonts"""

		self._pen_ruler_base  .setColor(self._palette.dark().color())
		self._pen_ruler_base  .setWidth(self._ruler_stroke)

		# Dark mode?
		if self._palette.window().color().value() > self._palette.windowText().color().value():
			kewl_color = self._palette.button().color().lighter(105)
		else:
			kewl_color = self._palette.button().color().darker(105)
		kewl_color.setAlphaF(DEFAULT_FANCY_ALPHA)

		self._brush_ruler_base.setColorAt(0.0, self._palette.light() .color())
		self._brush_ruler_base.setColorAt(0.1, self._palette.button().color().darker(110))
		self._brush_ruler_base.setColorAt(0.5, self._palette.button().color())
		self._brush_ruler_base.setColorAt(0.9, kewl_color)
		self._brush_ruler_base.setColorAt(1.0, self._palette.dark()  .color())

		self._pen_ruler_ticks .setColor(self._palette.buttonText().color())
		self._pen_ruler_ticks .setWidth(self._ruler_stroke)

		self._font_ruler_ticks = self._font

	def rulerSize(self) -> int:
		"""Size of the ruler"""

		return self._ruler_size
	
	@QtCore.Slot(int)
	def setRulerSize(self, ruler_size:int):

		if ruler_size != self._ruler_size:

			self._ruler_size = ruler_size
			self.sig_ruler_size_changed.emit(ruler_size)
			self.sig_update_requested.emit()

	def paintOverlay(self, painter, rect_canvas, rect_dirty):
		"""Do the paint"""

		#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

		for orientation in self._ruler_orientations:

			painter.save()

			self._draw_ruler_base(painter, rect_canvas, orientation)
			self._draw_ruler_ticks(painter, rect_canvas, orientation)
			self._draw_ruler_handle(painter, rect_canvas)

			painter.restore()

	def _draw_ruler_handle(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF):

		painter.save()

		painter.setPen(self._pen_ruler_base)
		painter.setBrush(self._palette.button())

		rect_handle = QtCore.QRectF(self._ruler_position, QtCore.QSizeF(self._ruler_size, self._ruler_size))
		rect_handle.translate(QtCore.QPointF(-self._ruler_stroke/2, -self._ruler_stroke/2))

		painter.drawRect(rect_handle)

		painter.restore()

	
	def _draw_ruler_base(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal):

		painter.save()

		ruler_rect = self.rulerRect(rect_canvas, orientation)
		
		if orientation == QtCore.Qt.Orientation.Horizontal:
			
			grad = QtGui.QLinearGradient(self._brush_ruler_base)
			grad.setStart(ruler_rect.topLeft())
			grad.setFinalStop(ruler_rect.bottomLeft())

		elif orientation == QtCore.Qt.Orientation.Vertical:
			
			grad = QtGui.QLinearGradient(self._brush_ruler_base)
			grad.setStart(ruler_rect.topLeft())
			grad.setFinalStop(ruler_rect.topRight())
			

		painter.setBrush(grad)
		painter.setPen(self._pen_ruler_base)
		painter.drawRect(ruler_rect)

		painter.restore()

	def _draw_ruler_ticks(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal):

		painter.save()
		
		ruler_rect = self.rulerRect(rect_canvas, orientation)
		painter.setClipRect(ruler_rect)
		
		painter.setPen(self._pen_ruler_ticks)
		painter.setFont(self._font_ruler_ticks)

		for tick_info in self._ruler_ticks[orientation]:

			if orientation == QtCore.Qt.Orientation.Horizontal:

				line_tick = QtCore.QLineF(
					QtCore.QPointF(tick_info.ruler_offset, ruler_rect.bottom() - self._ruler_tick_size),
					QtCore.QPointF(tick_info.ruler_offset, ruler_rect.bottom())
				)

				text_rect = QtCore.QRectF(
					ruler_rect.topLeft(),
					ruler_rect.size()
				)
				text_rect.moveCenter(QtCore.QPoint(tick_info.ruler_offset, ruler_rect.center().y()))

			elif orientation == QtCore.Qt.Orientation.Vertical:

				line_tick = QtCore.QLineF(
					QtCore.QPointF(ruler_rect.right() - self._ruler_tick_size, tick_info.ruler_offset),
					QtCore.QPointF(ruler_rect.right(), tick_info.ruler_offset)
				)

				text_rect = QtCore.QRectF(
					ruler_rect.topLeft(),
					ruler_rect.size()
				)
				text_rect.moveCenter(QtCore.QPoint(ruler_rect.center().x(), tick_info.ruler_offset))

			painter.drawLine(line_tick)

			painter.drawText( 
				text_rect,
				QtCore.Qt.AlignmentFlag.AlignCenter,
				tick_info.tick_label
			)

		painter.restore()
	
	def rulerRect(self, rect_canvas:QtCore.QRectF, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal) -> QtCore.QRectF:
		"""Given a viewport rect, get a rect of the current ruler area"""

		ruler_rect = QtCore.QRectF(rect_canvas)

		if orientation == QtCore.Qt.Orientation.Vertical:

			ruler_rect.setWidth(self._ruler_size)
			ruler_rect.adjust(
				-self._ruler_stroke/2,
				-self._ruler_stroke/2,
				-self._ruler_stroke/2,
				-self._ruler_stroke/2,
			)

			ruler_rect.translate(self._ruler_position.x(), 0)
		
		elif orientation == QtCore.Qt.Orientation.Horizontal:

			ruler_rect.setHeight(self._ruler_size)
			ruler_rect.adjust(
				-self._ruler_stroke/2,
				-self._ruler_stroke/2,
				-self._ruler_stroke/2,
				-self._ruler_stroke/2,
			)
			ruler_rect.translate(0, self._ruler_position.y())

		return ruler_rect