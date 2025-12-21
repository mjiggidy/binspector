from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSFrameViewConfig
from ..utils import stylewatcher

if TYPE_CHECKING:
	from ..frameview.frameview import BSBinFrameViewGridInfo

class BSBinFrameBackgroundPainter(QtCore.QObject):
	"""Draw the background grid on a frame view"""
	
	sig_enabled_changed = QtCore.Signal(bool)

	def __init__(self,
		parent:QtWidgets.QWidget,
		*args,
		grid_info:BSBinFrameViewGridInfo|None=None,
		tick_width_major:float=3,
		tick_width_minor:float=1.5,
		**kwargs
	):

		super().__init__(parent, *args, **kwargs)

		self._is_enabled = True

		self._grid_unit_info = grid_info or BSBinFrameViewGridInfo(
			unit_size      = BSFrameViewConfig.GRID_UNIT_SIZE,
			unit_divisions = BSFrameViewConfig.GRID_DIVISIONS,
		)

		self._watcher_style   = stylewatcher.BSWidgetStyleEventFilter(parent=self)
		parent.installEventFilter(self._watcher_style)

		self._pen_tick_major  = QtGui.QPen()
		self._pen_tick_minor  = QtGui.QPen()

		self._pen_tick_major.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen_tick_major.setCosmetic(True)
		self.setMajorTickWidth(tick_width_major)

		self._pen_tick_minor.setStyle(QtCore.Qt.PenStyle.DashLine)
		self._pen_tick_minor.setCosmetic(True)
		self.setMinorTickWidth(tick_width_minor)

		self.setPalette(parent.palette())
		self._watcher_style.sig_palette_changed.connect(self.setPalette)

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled):

		if self._is_enabled == is_enabled:
			return
		
		self._is_enabled = is_enabled
		self.sig_enabled_changed.emit(is_enabled)
	
	def isEnabled(self) -> bool:
		return self._is_enabled

	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

#		logging.getLogger(__name__).debug("Setting palette...")

		self._pen_tick_major.setColor(palette.alternateBase().color())
		self._pen_tick_minor.setColor(palette.alternateBase().color())

	@QtCore.Slot(object)
	def setGridInfo(self, grid_info:BSBinFrameViewGridInfo):

		self._grid_unit_info = grid_info

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setMajorTickWidth(self, tick_width_major:float):

		self._pen_tick_major.setWidthF(float(tick_width_major))

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setMinorTickWidth(self, tick_width_minor:float):

		self._pen_tick_minor.setWidthF(float(tick_width_minor))

	def drawBackground(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):

		if not self._is_enabled:
			return

		painter.save()

		self._draw_horizontal_grid(painter, rect_scene)
		self._draw_vertical_grid(painter, rect_scene)

		painter.restore()

	def _draw_horizontal_grid(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):
		# Horizontal
		# Align to grid divisions
		range_scene_start = rect_scene.left() - (rect_scene.left()  % self._grid_unit_info.unit_size.width())
		range_scene_end   = rect_scene.right()- (rect_scene.right() % self._grid_unit_info.unit_size.width()) + self._grid_unit_info.unit_size.width() # Overshoot by additional unit

		x_pos = range_scene_start
		while x_pos < range_scene_end:

			if not x_pos % self._grid_unit_info.unit_size.width():
				painter.setPen(self._pen_tick_major)
			else:
				painter.setPen(self._pen_tick_minor)

			painter.drawLine(QtCore.QLineF(
				QtCore.QPointF(x_pos, rect_scene.top()),
				QtCore.QPointF(x_pos, rect_scene.bottom())
			))

			x_pos += self._grid_unit_info.unit_step.x()

	def _draw_vertical_grid(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):

		# Vertical
		# Align to grid divisions
		range_scene_start = rect_scene.top() - (rect_scene.top()  % self._grid_unit_info.unit_size.height())
		range_scene_end   = rect_scene.bottom()- (rect_scene.bottom() % self._grid_unit_info.unit_size.height()) + self._grid_unit_info.unit_size.height() # Overshoot by additional unit

		y_pos = range_scene_start
		while y_pos < range_scene_end:

			if not y_pos % self._grid_unit_info.unit_size.height():
				painter.setPen(self._pen_tick_major)
			else:
				painter.setPen(self._pen_tick_minor)

			painter.drawLine(QtCore.QLineF(
				QtCore.QPointF(rect_scene.left(), y_pos),
				QtCore.QPointF(rect_scene.right(), y_pos)
			))

			y_pos += self._grid_unit_info.unit_step.y()