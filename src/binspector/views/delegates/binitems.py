import logging
from PySide6 import QtCore, QtGui, QtWidgets
from ...utils import drawing

class BSGenericItemDelegate(QtWidgets.QStyledItemDelegate):

	sig_padding_changed = QtCore.Signal(QtCore.QMargins)

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
			self.sig_padding_changed.emit(padding)
	

class LBClipColorItemDelegate(BSGenericItemDelegate):
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

		# Correct for padding
		canvas_active = canvas.marginsRemoved(self._padding)

		canvas_active.setWidth(canvas_active.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()))
		canvas_active = canvas_active.marginsRemoved(self._margins)
		canvas_active.moveCenter(option.rect.center())
		
		painter.save()

		try:
			drawing.draw_clip_color_chip(
				painter=painter,
				canvas=canvas_active,
				clip_color=clip_color,
				#border_color=option.palette.color(QtGui.QPalette.ColorRole.WindowText),
				border_color=QtGui.QColor("Black"),
				border_width=1,
				#shadow_color=option.palette.color(QtGui.QPalette.ColorRole.Shadow),
				shadow_color=QtGui.QColor("Black"),
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