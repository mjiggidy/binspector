import logging
from PySide6 import QtCore, QtGui, QtWidgets
from ...utils import drawing

class BSGenericItemDelegate(QtWidgets.QStyledItemDelegate):

	def __init__(self, padding:QtCore.QMargins|None=None, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._padding = padding or QtCore.QMargins()

	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSize:
		
		hint_og = super().sizeHint(option, index)
		
		return QtCore.QSize(
			hint_og.width()  + self._padding.left() + self._padding.right(),
			hint_og.height() + self._padding.top()  + self._padding.bottom()
		)
	
	def setPadding(self, padding:QtCore.QMargins):

		if self._padding != padding:
		
			self._padding = padding
			self.sizeHintChanged.emit(padding)
	

class LBClipColorItemDelegate(BSGenericItemDelegate):
	"""Draw a clip color chip(?) to a give painter"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._margins      = QtCore.QMargins(*[4]*4)
		self._aspect_ratio = QtCore.QSize(4,3)

	def sizeHint(self, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex) -> QtCore.QSize:

		orig = super().sizeHint(option, index)

		# Return aspect ratio-corrected width x original height
		return QtCore.QSize(orig.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()), orig.height())

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		super().paint(painter, option, index)

		# "No clip color" should at least be an invalid `QtCore.QColor`
		clip_color = index.data(QtCore.Qt.ItemDataRole.UserRole)
		if not isinstance(clip_color, QtGui.QColor):
			logging.getLogger(__name__).error("Skipping clip color delegate because UserRole was not QColor (got %s)", type(clip_color).__name__)
			return
		
		# Center, size and shape the canvas QRect
		canvas_active = option.rect.marginsRemoved(self._padding)
		canvas_active.setWidth(
			min(
				canvas_active.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()),
				canvas_active.width() - self._padding.left() - self._padding.right()
			)
		)
		canvas_active.moveCenter(option.rect.center())
		
		painter.save()

		#painter.fillRect(canvas_active, QtGui.QColor("Black"))

		try:
			drawing.draw_clip_color_chip(
				painter=painter,
				canvas=canvas_active,
				clip_color=clip_color,
				#border_color=option.palette.color(QtGui.QPalette.ColorRole.WindowText),
				border_color=option.palette.color(QtGui.QPalette.ColorRole.WindowText),
				border_width=1,
				#shadow_color=option.palette.color(QtGui.QPalette.ColorRole.Shadow),
				shadow_color=option.palette.color(QtGui.QPalette.ColorRole.Shadow),
			)
		except Exception as e:
			print(e)
			logging.getLogger(__name__).error("Error drawing clip color delegate: %s", e)

		painter.restore()

class LBTimecodeItemDelegate(BSGenericItemDelegate):
	"""Eventually imma want to"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex):
		
		super().paint(painter, option, index)