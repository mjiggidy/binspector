import logging
from PySide6 import QtCore, QtGui, QtWidgets
from ...utils import drawing
	

class LBClipColorItemDelegate(QtWidgets.QStyledItemDelegate):
	"""Draw a clip color chip(?) to a give painter"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._margins      = QtCore.QMargins(*[4]*4)
		self._aspect_ratio = QtCore.QSize(4,3)

	def sizeHint(self, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex) -> QtCore.QSize:

		# Width is height * aspect ratio
		orig = super().sizeHint(option, index)
		return QtCore.QSize(orig.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()), orig.height())
		#return QtCore.QSize(orig.height(), orig.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()))

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		super().paint(painter, option, index)
		
		# "No clip color" should at least be an invalid `QtCore.QColor`
		clip_color = index.data(QtCore.Qt.ItemDataRole.UserRole)
		if not isinstance(clip_color, QtGui.QColor):
			logging.getLogger(__name__).debug("Skipping clip color delegate because UserRole was not QColor (got %s)", type(clip_color).__name__)
			return
		
		# Center, size and shape the canvas QRect
		canvas = QtCore.QRect(option.rect)
		canvas.setWidth(canvas.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()))
		canvas = canvas.marginsRemoved(self._margins)
		canvas.moveCenter(option.rect.center())
		
		painter.save()

		try:
			drawing.draw_clip_color_chip(
				painter=painter,
				canvas=canvas,
				clip_color=clip_color,
				border_color=option.palette.color(QtGui.QPalette.ColorRole.WindowText),
				border_width=1,
				shadow_color=option.palette.color(QtGui.QPalette.ColorRole.Shadow)
			)
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing clip color delegate: %s", e)

		painter.restore()

class LBTimecodeItemDelegate(QtWidgets.QStyledItemDelegate):
	"""Eventually imma want to"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex):
		
		super().paint(painter, option, index)