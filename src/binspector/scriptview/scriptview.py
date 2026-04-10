"""
Script View Mode
"""

from PySide6 import QtCore, QtGui, QtWidgets

from ..textview import textview
from ..binitems import binitemtypes
from ..binwidget import itemdelegates

from ..core.config import BSScriptViewModeConfig
from ..utils import drawing

import avbutils


class BSBinScriptView(textview.BSBinTextView):

	sig_frame_scale_changed = QtCore.Signal(float)
	sig_frame_size_changed  = QtCore.Signal(QtCore.QSize)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._frame_delegate     = itemdelegates.BSFrameThumbnailDelegate(aspect_ratio=QtCore.QSizeF(16, 9), frame_scale=BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_START*100)

		self.header().setSectionsMovable(False)

		self._delegate_provider.setUniqueDelegateForField(avbutils.bins.BinColumnFieldIDs.Frame, self._frame_delegate)

		# Need to repaint entire viewport when scrolling, due to drawRow()
		self.verticalScrollBar()  .valueChanged.connect(self.viewport().update)
		self.horizontalScrollBar().valueChanged.connect(self.viewport().update)

	@QtCore.Slot(object)
	def setFrameScale(self, frame_scale:float):
		
		if frame_scale == self._frame_delegate.frameScale():
			return
		
		self._frame_delegate.setFrameScale(frame_scale)
		self.scheduleDelayedItemsLayout()
		self.header().setSectionResizeMode(self.header().logicalIndex(0), QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.sig_frame_scale_changed.emit(frame_scale)

	def frameScale(self) -> float:
		"""The scale factor for the frame rect"""

		return self._frame_delegate.frameScale()

	@QtCore.Slot(QtCore.QSize)
	def setFrameAspectRatio(self, aspect_ratio:QtCore.QSize|QtCore.QSizeF):

		if self._frame_delegate.aspectRatio() == aspect_ratio:
			return
		
		self._frame_delegate.setAspectRatio(aspect_ratio)
		self.updateGeometries()
		self.viewport().update()

		self.sig_frame_size_changed.emit(aspect_ratio)

	def frameAspectRatio(self) -> QtCore.QSize|QtCore.QSizeF:
		"""Base frame size at `scale=1.0`"""
		
		return self._frame_delegate.aspectRatio()
	

	def drawRow(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
		

		super().drawRow(painter, option, index)



		frame_rect = QtCore.QRect(
			QtCore.QPoint(option.rect.left() + self._frame_delegate.itemPadding().left(), option.rect.top() + self._frame_delegate.itemPadding().top()),
			QtCore.QSize(self._frame_delegate.aspectRatio().width() * self._frame_delegate.frameScale(), self._frame_delegate.aspectRatio().height() * self._frame_delegate.frameScale())
		)

		clip_color = index.data(binitemtypes.BSBinItemDataRoles.ClipColorRole)

		frame_offset = index.data(binitemtypes.BSBinItemDataRoles.FrameThumbnailRole)
		shadow_color:QtGui.QColor = option.palette.color(QtGui.QPalette.ColorRole.Shadow)
		shadow_color.setAlphaF(0.25)

		drawing.draw_frame_thumbnail(
			painter=painter,
			canvas=frame_rect,
			frame_offset=frame_offset,
			base_color = QtGui.QColor(32,32,32),
			clip_color = clip_color,
			shadow_color=shadow_color
		)



		# Gather required data

		script_text     = index.data(role=binitemtypes.BSBinItemDataRoles.ScriptNotesRole) or "Nah"
		item_delegate   = self._delegate_provider.delegateForColumn(index.column())
		row_is_selected = self.selectionModel().isSelected(index)

		# Build rects

		if not self.model() or not self.model().columnCount(QtCore.QModelIndex()) > 1:
			return

		offset_left = frame_rect.right() + self._frame_delegate.itemPadding().right()
#		print("** Offset", offset_left)

		script_rect = QtCore.QRectF(
			QtCore.QPointF(
				offset_left + item_delegate.itemPadding().left(),
				option.rect.top() + item_delegate.itemPadding().top() + option.fontMetrics.height() + item_delegate.itemPadding().top(),
			),

			QtCore.QPointF(
				option.rect.right() - item_delegate.itemPadding().right(),
				option.rect.bottom() - item_delegate.itemPadding().top(),
			)
		)

		# Draw em

		pen = QtGui.QPen()
		
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setColor(
			option.palette.highlightedText().color() \
			  if row_is_selected \
			  else option.palette.windowText().color()
		)

		brush = QtGui.QBrush()
		brush.setColor(option.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.save()
		
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.setFont(option.font)

#		if row_is_selected:
		painter.drawRect(script_rect)
		
#		painter.drawRect(frame_rect)

		if script_text:
			pen.setColor(option.palette.windowText().color())
			painter.setPen(pen)
			painter.drawText(script_rect, script_text)


		painter.restore()