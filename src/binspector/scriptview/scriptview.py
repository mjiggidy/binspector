from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSScriptViewConfig

from ..listview import listview
import avbutils

class BSBinScriptView(listview.BSBinListView):
	"""Script view"""

	sig_frame_scale_changed       = QtCore.Signal(float)
	sig_frame_scale_range_changed = QtCore.Signal(float) # TODO
	sig_item_padding_changed      = QtCore.Signal(QtCore.QMarginsF)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.header().setSectionsMovable(False)
		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.SingleSelection)
		self.setSortingEnabled(False)
		self.setDragEnabled(True)
		#self.setAlternatingRowColors(False)

		self._frame_size  = QtCore.QSizeF(16, 9)
		self._frame_scale = BSScriptViewConfig.DEFAULT_SCRIPT_ZOOM_START

		self._item_padding = BSScriptViewConfig.DEFAULT_ITEM_PADDING
		
		self.applyHeaderConstraints()

	@QtCore.Slot(object)
	def setFrameScale(self, frame_scale:float):
		
		if frame_scale == self._frame_scale:
			return
		
		self._frame_scale = frame_scale

		self.applyHeaderConstraints()
		self.updateDelegates()

		self.sig_frame_scale_changed.emit(frame_scale)

		self.viewport().update()

	def frameScale(self) -> float:
		"""The scale factor for the frame rect"""

		return self._frame_scale
	
	def frameRect(self) -> QtCore.QRectF:
		"""The frame rect"""

		return QtCore.QRectF(
			QtCore.QPointF(0,0),
			QtCore.QPointF(
				self._frame_size.width() * self._frame_scale,
				self._frame_size.height() * self._frame_scale
			)
		)
	
	@QtCore.Slot(QtCore.QMarginsF)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		"""Set item padding and add frame size padding"""

		if self._item_padding == padding:
			import logging
			logging.getLogger(__name__).error("NO %s", str(padding))
			return
		
		self._item_padding = padding

		#print("ITEM PADDING NOW", self._item_padding)

		self.applyHeaderConstraints()
		self.updateDelegates()
		
		self.sig_item_padding_changed.emit(padding)

	def updateDelegates(self):

		script_pad = QtCore.QMarginsF(self._item_padding)
		old_pad = QtCore.QMarginsF(script_pad)
		script_pad.setBottom(max(
			self.frameRect().height(),
			self._item_padding.bottom()

		))

		#print(f"{old_pad=} {script_pad=}")

		for col in range(self.header().count()):
			self.itemDelegateForColumn(col).setItemPadding(script_pad)

	def applyHeaderConstraints(self):
		"""Header constraints"""

		self.resizeColumnToContents(self.header().logicalIndex(0))

		# Resize first section to accomodate frame
		self.header().resizeSection(
			self.header().logicalIndex(0),
			self.header().sectionSize(self.header().logicalIndex(0)) + self.frameRect().width() + 16
		)

	def rowsInserted(self, parent:QtCore.QModelIndex, start:int, end:int):
		pass
		
#		for row in range(start, end+1):
#			
#			idx_row = self.model().index(row, 0, parent)
#			delegate = self.itemDelegate(idx_row)
#			delegate = delegate.__class__(delegate)
#		#	delegate.setItemPadding(QtCore.QMargins(5,5, 5, 500))		
#
#		#	self.setItemDelegateForColumn(0, delegate)	

	def drawRow(self, painter:QtGui.QPainter, options:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
		
		
		item_delegate = self.itemDelegate(index)
		
		super().drawRow(painter, options, index)


		#print(f"{options.rect=} {item_delegate.itemPadding()=}")

		frame_rect = self.frameRect().translated(
			QtCore.QPointF(
				options.rect.left() + self._item_padding.left(),
				options.rect.top()  +self._item_padding.top(),
			)
		)

		fields      = index.model().sourceModel().fields()

		field_index = fields.index(str(avbutils.BIN_COLUMN_ROLES["Name"]))
		src_index   = index.model().mapToSource(index)

		script_text = src_index.siblingAtColumn(field_index).data(QtCore.Qt.ItemDataRole.DisplayRole)

		script_rect = QtCore.QRectF(
			QtCore.QPointF(
				frame_rect.right() + item_delegate.itemPadding().left(),
				options.rect.bottom() - item_delegate.itemPadding().bottom(),
			),

			QtCore.QPointF(
				options.rect.right() - item_delegate.itemPadding().right(),
				options.rect.bottom() - item_delegate.itemPadding().top(),
			)
		)

		pen = QtGui.QPen()
		pen.setColor(options.palette.windowText().color())
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

		brush = QtGui.QBrush()
		brush.setColor(options.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.save()
		
		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRect(script_rect)
		painter.drawText(script_rect, script_text)

		painter.drawRect(frame_rect)

		painter.restore()

#		self.viewport().update(options.rect) # NOTE: Not just active_rect -- Scrolling needs to repaint the whole thing