import logging, typing
from PySide6 import QtCore, QtGui, QtWidgets

from ..core  import icon_providers


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

		if self._padding == padding:
			return

		self._padding = QtCore.QMarginsF(padding)

		# NOTE: Binding to sizeHintChanged here to trigger redraw
		# Passing invalid model index seems to work ok
		self.sizeHintChanged.emit(QtCore.QModelIndex())
	
	def itemPadding(self) -> QtCore.QMargins:

		return self._padding

	def activeRectFromRect(self, rect:QtCore.QRectF) -> QtCore.QRectF:
		"""The active area without padding and such"""

		return QtCore.QRectF(rect).marginsRemoved(self._padding)
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		kewl_options = QtWidgets.QStyleOptionViewItem(option)
		self.initStyleOption(kewl_options, index)

		kewl_text = kewl_options.text

		# Remove focus and text for a generic paint from drawControl()
		kewl_options.state &= ~QtWidgets.QStyle.State_HasFocus
		kewl_options.text = ""

		style = kewl_options.widget.style() if kewl_options.widget else QtWidgets.QApplication.style()
		style.drawControl(QtWidgets.QStyle.ControlElement.CE_ItemViewItem, kewl_options, painter)

		# Pull in rect adjusted for padding; text for paint
		kewl_options.rect = self.activeRectFromRect(option.rect).toRect()
		kewl_options.text = option.text

		fm = QtGui.QFontMetrics(kewl_options.font)
		elided_text = fm.elidedText(kewl_text, kewl_options.textElideMode, kewl_options.rect.width())
		
		# NOTE HERE: Uh so yeah this is redrawing a bunch at the smaller rect and I only really need text but lol
		painter.setFont(kewl_options.font)
		style.drawItemText(
			painter,
			kewl_options.rect,
			int(kewl_options.displayAlignment),
			kewl_options.palette,
			bool(kewl_options.state & QtWidgets.QStyle.StateFlag.State_Enabled),
			elided_text,
			QtGui.QPalette.ColorRole.HighlightedText if bool(kewl_options.state & QtWidgets.QStyle.StateFlag.State_Selected) else QtGui.QPalette.ColorRole.Text
		)

		# DEBUG:
		#painter.drawRect(kewl_options.rect)

		#return super().paint(painter, kewl_options, index)

	def clone(self, *args, **kwargs) -> typing.Self:

		return self.__class__(self._padding, *args, **kwargs)

class BSIconLookupItemDelegate(BSGenericItemDelegate):
	"""Displays an icon centered in its item rect, with padding and aspect ratio preservation or something"""

	def __init__(self, *args, aspect_ratio:QtCore.QSizeF|None=None, icon_provider:icon_providers.BSIconProvider|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._aspect_ratio  = aspect_ratio  or QtCore.QSizeF(1,1)
		self._icon_provider = icon_provider or icon_providers.BSIconProvider()

	def iconProvider(self) -> icon_providers.BSIconProvider:
		return self._icon_provider

	def sizeWithAspectRatio(self, rect:QtCore.QSize) -> QtCore.QSize:
		"""Over-engineering?  Probably.  Return a size corrected for aspect ratio with priority given to height."""

		return QtCore.QSize(
			rect.height() * (self._aspect_ratio.width()/self._aspect_ratio.height()),
			rect.height()
		)

	def sizeHint(self, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex) -> QtCore.QSize:
		"""Return aspect ratio-corrected width x original height"""

		orig_size = super().sizeHint(option, index)

		# HACKY, BUT:
		adj_size = QtCore.QSize(
			orig_size.width() - self._padding.left() - self._padding.right(),
			orig_size.height() - self._padding.top() - self._padding.bottom()
		)

		adj_size  = self.sizeWithAspectRatio(adj_size)

		print("ADJ SIZE IS ", adj_size, " from orig",orig_size)
		
		# NOTE: This was killing me for a while.  Adding back in the horizontal padding
		# after correcting horizontal aspect ratio based on height.  I'm dumb.
		adj_size += QtCore.QSize(self._padding.left() + self._padding.right(), 0)
		
		return adj_size
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		self.initStyleOption(option, index)
		style = option.widget.style() if option.widget else QtWidgets.QApplication.style()
		
		user_data = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
		icon      = self._icon_provider.getIcon(user_data)

		# Center, size and shape the canvas QRect
		canvas_active = self.activeRectFromRect(option.rect)#.marginsRemoved(self._padding)
		
		# NOTE: Based on the active canvas area, bind the width to
		# Min: Same as height (square)
		# Max: Aspect ratio (w * w/h)
		w_min = canvas_active.height()
		w_max = canvas_active.height() * (self._aspect_ratio.width() / self._aspect_ratio.height())
		if canvas_active.width() < canvas_active.height():
			w_active = w_min
		elif canvas_active.width() > w_max:
			w_active = w_max
		else:
			w_active = canvas_active.width()
		
		canvas_active.setWidth(w_active)
		canvas_active.moveCenter(QtCore.QRectF(option.rect).marginsRemoved(self._padding).center())
		
		painter.save()
		painter.setClipRect(option.rect)
		
		# DEBUG
		painter.drawRect(QtCore.QRect(option.rect.topLeft(), self.sizeHint(option, index)))
		#painter.drawRect()
		
		try:
			style.drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

			icon.paint(
				painter,
				canvas_active.toRect(),
				mode=QtGui.QIcon.Mode.Selected if option.state & QtWidgets.QStyle.StateFlag.State_Selected else QtGui.QIcon.Mode.Active,
				state=QtGui.QIcon.State.On     if option.state & QtWidgets.QStyle.StateFlag.State_On       else QtGui.QIcon.State.Off,
			)
		
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing icon: %s", e)
		
		painter.restore()

	def clone(self) -> typing.Self:

	#	print("OKAY HERE I GOOO")

		return self.__class__(
			aspect_ratio = QtCore.QSizeF(self._aspect_ratio),
			icon_provider = self._icon_provider,
			padding = QtCore.QMarginsF(self._padding),
		)