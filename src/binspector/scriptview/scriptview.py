"""
Script View Mode
"""

from PySide6 import QtCore, QtGui, QtWidgets

from ..textview import textview
from ..binitems import binitemtypes
from ..binwidget import itemdelegates

from ..core.config import BSScriptViewModeConfig

import avbutils


class BSBinScriptViewNEWGOOD(textview.BSBinTextView):

	sig_frame_scale_changed = QtCore.Signal(float)
	sig_frame_size_changed  = QtCore.Signal(QtCore.QSize)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._frame_delegate     = itemdelegates.BSFrameThumbnailDelegate(aspect_ratio=QtCore.QSizeF(16, 9), frame_scale=BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_START*100)

		self.header().setSectionsMovable(False)
#		self.setUniformRowHeights(False)

		self._delegate_provider.setUniqueDelegateForField(avbutils.bins.BinColumnFieldIDs.Frame, self._frame_delegate)

	@QtCore.Slot(object)
	def setFrameScale(self, frame_scale:float):
		
		if frame_scale == self._frame_delegate.frameScale():
			return
		
		self._frame_delegate.setFrameScale(frame_scale)
#		self.updateGeometries()
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
	

	def drawRow(self, painter:QtGui.QPainter, options:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
		

		super().drawRow(painter, options, index)

#		print("** FONT METS", options.fontMetrics.height())

		# Gather required data

		script_text     = index.data(role=binitemtypes.BSBinItemDataRoles.ScriptNotesRole) or "Nah"
		item_delegate   = self._delegate_provider.delegateForColumn(index.column())
		row_is_selected = self.selectionModel().isSelected(index)

		# Build rects

		if not self.model() or not self.model().columnCount(QtCore.QModelIndex()) > 1:
			return

		offset_left = self.visualRect(index.siblingAtColumn(0)).right()
#		print("** Offset", offset_left)

		script_rect = QtCore.QRectF(
			QtCore.QPointF(
				offset_left + item_delegate.itemPadding().left(),
				options.rect.top() + item_delegate.itemPadding().top() + options.fontMetrics.height() + item_delegate.itemPadding().top(),
			),

			QtCore.QPointF(
				options.rect.right() - item_delegate.itemPadding().right(),
				options.rect.bottom() - item_delegate.itemPadding().top(),
			)
		)

		# Draw em

		pen = QtGui.QPen()
		
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setColor(
			options.palette.highlightedText().color() \
			  if row_is_selected \
			  else options.palette.windowText().color()
		)

		brush = QtGui.QBrush()
		brush.setColor(options.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.save()
		
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.setFont(options.font)

#		if row_is_selected:
		painter.drawRect(script_rect)
		
#		painter.drawRect(frame_rect)

		if script_text:
			pen.setColor(options.palette.windowText().color())
			painter.setPen(pen)
			painter.drawText(script_rect, script_text)


		painter.restore()

































class BSBinScriptViewDEPRECATEDBAD(textview.BSBinTextView):
	"""Script view"""

	sig_frame_scale_changed       = QtCore.Signal(float)
	sig_frame_scale_range_changed = QtCore.Signal(float) # TODO


	def __init__(self, *args, **kwargs):

		self._frame_size   = QtCore.QSizeF(16, 9) * 2
		self._frame_scale  = BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_START
		
		super().__init__(*args, **kwargs)

		return

		#self.setAlternatingRowColors(False)

		# Need to repaint entire viewport when scrolling, due to drawRow()
		self.verticalScrollBar()  .valueChanged.connect(self.viewport().update)
		self.horizontalScrollBar().valueChanged.connect(self.viewport().update)


# DISABLING FOR NOW
# I HATE YOU
#		self.setItemPadding(BSScriptViewModeConfig.DEFAULT_ITEM_PADDING)
#	
#		self.applyHeaderConstraints()

	@QtCore.Slot(QtCore.QMarginsF)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		#print("Please help me oh god")
		super().setItemPadding(padding)

		for delegate in self._delegate_provider.delegates():

			padding= delegate.itemPadding()
			padding.setBottom(self._bottomItemPadding())
			delegate.setItemPadding(padding)

		self.adjustFirstItemPadding()

		# NOTE: These `scheduleDelayedItemsLayout` calls MIGHT be because
		# of the proxy delegate not sending update() or something...?
		self.scheduleDelayedItemsLayout()

	def syncFromHeader(self, header:QtWidgets.QHeaderView):
		"""Sync header from another header"""

		self.header().restoreState(
			header.saveState()
		)
		self.applyHeaderConstraints()

	@QtCore.Slot(object)
	def setFrameScale(self, frame_scale:float):
		
		if frame_scale == self._frame_scale:
			return
		
		self._frame_scale = frame_scale
		
		self.adjustFirstItemPadding()
		self.applyHeaderConstraints() # NOTE: Not needed / complicates scaling
		self.setItemPadding(self._item_padding)

		# Re-draw drawRow()
		#self.viewport().update()

		self.sig_frame_scale_changed.emit(frame_scale)

	def frameScale(self) -> float:
		"""The scale factor for the frame rect"""

		return self._frame_scale
	
	def frameRect(self) -> QtCore.QRectF:
		"""The frame rect"""

		return QtCore.QRectF(
			QtCore.QPointF(0,0),
			QtCore.QPointF(
				self._frame_size.width() * self._frame_scale/BSScriptViewModeConfig.FRAME_SIZE_SCALER,
				self._frame_size.height() * self._frame_scale/BSScriptViewModeConfig.FRAME_SIZE_SCALER,
			)
		)

	def _firstItemOffset(self) -> float:

		return self._item_padding.left() + self.frameRect().width() + self._item_padding.right()
	
	def _bottomItemPadding(self) -> float:
		"""Calculated bottom padding for item delegate which factors in the frame"""

		
		# NOTE: Using self.font() is tenuous here, using the view's font instead of the delegates
		# but uhhhhh good foooor noowwww...???
		return self.frameRect().height() + self._item_padding.bottom() - QtGui.QFontMetricsF(self.font()).height()

	def adjustFirstItemPadding(self):
		"""Adjust the first item delegate's padding to make room for frame stuff"""

#		print("Left padding setting to ", self._firstItemOffset())
		new_padding = QtCore.QMarginsF(self._item_padding)

		first_col_log = self.header().logicalIndex(0)

		
		first_del = self._delegate_provider.delegateForColumn(first_col_log)
		first_del = first_del.clone()


		new_padding.setLeft(self._firstItemOffset())
		new_padding.setBottom(self._bottomItemPadding())
		first_del.setItemPadding(new_padding)

		self._delegate_provider.setDelegateForColumn(first_col_log, first_del)

		#first_del = self._delegate_provider.delegateForColumn(first_col_log)
		#print("**** SEtting first item paddin gfor", self.model().headerData(0, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole), "to", new_padding)

		

	def applyHeaderConstraints(self):
		"""Header constraints"""

		# Since I copy header from list view to script view, need to restore a lot of constraints

		# Apply different resize mode to first column (old)
#		first_col_log = self.header().logicalIndex(0)
#		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
#		self.header().setSectionResizeMode(first_col_log, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

		self.header().setSectionsMovable(False)
		self.setSortingEnabled(False)
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.SingleSelection)
		self.setDragEnabled(True)

		self.header().setSectionResizeMode(BSScriptViewModeConfig.DEFAULT_COLUMN_RESIZE_MODE)

	def drawRow(self, painter:QtGui.QPainter, options:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
		

		super().drawRow(painter, options, index)

		# Gather required data

		script_text     = index.data(role=binitemtypes.BSBinItemDataRoles.ScriptNotesRole)
		item_delegate   = self._delegate_provider.delegateForColumn(index.column())
		row_is_selected = self.selectionModel().isSelected(index)

		# Build rects
		
		frame_rect =self.frameRect().translated(
			QtCore.QPointF(
				options.rect.left() + self._item_padding.left(),
				options.rect.top() + self._item_padding.top()
			)
		)

		script_rect = QtCore.QRectF(
			QtCore.QPointF(
				self._firstItemOffset(),
				options.rect.bottom() - item_delegate.itemPadding().bottom() + item_delegate.itemPadding().top(),
			),

			QtCore.QPointF(
				options.rect.right() - item_delegate.itemPadding().right(),
				frame_rect.bottom()
			)
		)

		# Draw em

		pen = QtGui.QPen()
		
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setColor(
			options.palette.highlightedText().color() \
			  if row_is_selected \
			  else options.palette.windowText().color()
		)

		brush = QtGui.QBrush()
		brush.setColor(options.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.save()
		
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.setFont(options.font)

		if row_is_selected:
			painter.drawRect(script_rect)
		
		painter.drawRect(frame_rect)

		if script_text:
			pen.setColor(options.palette.windowText().color())
			painter.setPen(pen)
			painter.drawText(script_rect, script_text)


		painter.restore()