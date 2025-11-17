import logging
from PySide6 import QtCore, QtGui, QtWidgets
from ...utils import drawing
from ...core  import icons

class BSGenericItemDelegate(QtWidgets.QStyledItemDelegate):

	def __init__(self, padding:QtCore.QMargins|None=None, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._padding = padding or QtCore.QMargins()

	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSize:
		"""Return size hint with padding factored in"""
		
		hint_og = super().sizeHint(option, index)
		
		return QtCore.QSize(
			hint_og.width()  + self._padding.left() + self._padding.right(),
			hint_og.height() + self._padding.top()  + self._padding.bottom()
		)
	
	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMargins):
		"""Set padding around individual items"""

		if self._padding != padding:
			self._padding = padding

			# NOTE: Binding to sizeHintChanged here to trigger redraw
			# Passing invalid model index seems to work ok
			self.sizeHintChanged.emit(QtCore.QModelIndex())
			

	def activeRectFromRect(self, rect:QtCore.QRect) -> QtCore.QRect:
		"""The active area without padding and such"""

		#return rect
		#print(self._padding)
		#print(rect.marginsRemoved(self._padding))
		return rect.marginsRemoved(self._padding)
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		kewl_options = QtWidgets.QStyleOptionViewItem(option)
		self.initStyleOption(kewl_options, index)

		kewl_options.state &= ~QtWidgets.QStyle.State_HasFocus
		kewl_text = kewl_options.text
		kewl_options.text = ""

		style = kewl_options.widget.style() if kewl_options.widget else QtWidgets.QApplication.style()
		style.drawControl(QtWidgets.QStyle.ControlElement.CE_ItemViewItem, kewl_options, painter)

		#super().paint(painter, kewl_options, index)

		kewl_rect = self.activeRectFromRect(kewl_options.rect)
		kewl_options.rect = kewl_rect
		kewl_options.text = kewl_text
		
		# NOTE HERE: Uh so yeah this is redrawing a bunch at the smaller rect and I only really need text but lol
		super().paint(painter, kewl_options, index)

		#return super().paint(painter, my_kewl_options, index)

class BSIconLookupItemDelegate(BSGenericItemDelegate):

	def __init__(self, *args, aspect_ratio:QtCore.QSize|None=None, icon_provider:icons.BSIconProvider|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._aspect_ratio  = aspect_ratio or QtCore.QSize(1,1)
		self._icon_provider = icon_provider or icons.BSIconProvider()

	def iconProvider(self) -> icons.BSIconProvider:
		return self._icon_provider

	def sizeWithAspectRatio(self, rect:QtCore.QSize) -> QtCore.QSize:
		"""Over-engineering?  Probably.  Return a size corrected for aspect ratio with priority given to height."""

		return QtCore.QSize(rect.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()), rect.height())

	def sizeHint(self, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex) -> QtCore.QSize:
		"""Return aspect ratio-corrected width x original height"""

		orig = super().sizeHint(option, index)
		adj  = self.sizeWithAspectRatio(orig)
		print(f"{orig=} {adj=}")
		return orig
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		opt = QtWidgets.QStyleOptionViewItem(option)
		self.initStyleOption(opt, index)
		style = opt.widget.style() if opt.widget else QtWidgets.QApplication.style()
		
		user_data = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
		icon      = self._icon_provider.getIcon(user_data)

		# Center, size and shape the canvas QRect
		canvas_active = self.activeRectFromRect(opt.rect)
		canvas_active.setWidth(
			min(
				canvas_active.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()),                # Full aspect ratio, or...
				max(canvas_active.height(), canvas_active.width() - self._padding.left() - self._padding.right()) # ...clamp to smaller width
			)
		)
		canvas_active.moveCenter(opt.rect.center())
		
		painter.save()
		
		try:
			style.drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, opt.widget)
			icon.paint(
				painter,
				canvas_active
			)
		
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing icon: %s", e)
		
		painter.restore()

class LBClipColorItemDelegate(BSGenericItemDelegate):
	"""Draw a clip color chip(?) to a give painter"""

	def __init__(self, *args, aspect_ratio:QtCore.QSize|None=None, border_width:int=1, **kwargs):

		raise DeprecationWarning("Use BSIconLookupItemDelegate instead there, hoss")

		super().__init__(*args, **kwargs)

		self._aspect_ratio = aspect_ratio or QtCore.QSize(4,3)
		self._border_width = border_width

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
		canvas_active = self.activeRectFromRect(option.rect)
		canvas_active.setWidth(
			min(
				canvas_active.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()),        # Full aspect ratio, or...
				max(canvas_active.height(), canvas_active.width() - self._padding.left() - self._padding.right() + self._border_width) # ...clamp to smaller width
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
				border_color=option.palette.color(QtGui.QPalette.ColorRole.WindowText),
				border_width=self._border_width,
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