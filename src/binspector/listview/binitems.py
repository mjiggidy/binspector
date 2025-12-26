import logging
from PySide6 import QtCore, QtGui, QtWidgets

from ..core  import icons

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

		#print)
		
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

		#return super().paint(painter, kewl_options, index)

class BSIconLookupItemDelegate(BSGenericItemDelegate):
	"""Displays an icon centered in its item rect, with padding and aspect ratio preservation or something"""

	def __init__(self, *args, aspect_ratio:QtCore.QSize|None=None, icon_provider:icons.BSIconProvider|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._aspect_ratio  = aspect_ratio  or QtCore.QSize(1,1)
		self._icon_provider = icon_provider or icons.BSIconProvider()

	def iconProvider(self) -> icons.BSIconProvider:
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
		adj_size  = self.sizeWithAspectRatio(orig_size)
		
		# NOTE: This was killing me for a while.  Adding back in the horizontal padding
		# after correcting horizontal aspect ratio based on height.  I'm dumb.
		adj_size += QtCore.QSize(self._padding.left() + self._padding.right(), 0)
		
		return adj_size
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		opt_styled = QtWidgets.QStyleOptionViewItem(option)
		self.initStyleOption(opt_styled, index)
		style = opt_styled.widget.style() if opt_styled.widget else QtWidgets.QApplication.style()
		
		user_data = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
		icon      = self._icon_provider.getIcon(user_data)

		# Center, size and shape the canvas QRect
		canvas_active = self.activeRectFromRect(opt_styled.rect)
		
		# Based on the active canvas area, bind the width to
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
		canvas_active.moveCenter(opt_styled.rect.center())
		
		painter.save()
		painter.setClipRect(opt_styled.rect)
		
		try:
			style.drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_PanelItemViewItem, opt_styled, painter, opt_styled.widget)

			icon.paint(
				painter,
				canvas_active.toRect(),
				mode=QtGui.QIcon.Mode.Selected if opt_styled.state & QtWidgets.QStyle.StateFlag.State_Selected else QtGui.QIcon.Mode.Active,
				state=QtGui.QIcon.State.On     if opt_styled.state & QtWidgets.QStyle.StateFlag.State_On       else QtGui.QIcon.State.Off,
			)
		
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing icon: %s", e)
		
		painter.restore()

class LBTimecodeItemDelegate(BSGenericItemDelegate):
	"""Eventually imma want to"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex):
		
		super().paint(painter, option, index)