from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSScriptViewConfig

from ..listview import listview
from ..binwidget import delegate_lookup
import avbutils

class BSBinScriptView(listview.BSBinListView):
	"""Script view"""

	sig_frame_scale_changed       = QtCore.Signal(float)
	sig_frame_scale_range_changed = QtCore.Signal(float) # TODO
	sig_item_padding_changed      = QtCore.Signal(QtCore.QMarginsF)


	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)


		#self.setAlternatingRowColors(False)

		self.verticalScrollBar().valueChanged.connect(self.viewport().update)
		self.horizontalScrollBar().valueChanged.connect(self.viewport().update)

		self._frame_size  = QtCore.QSizeF(16, 9) * 2
		self._frame_scale = BSScriptViewConfig.DEFAULT_SCRIPT_ZOOM_START

		self._item_padding = BSScriptViewConfig.DEFAULT_ITEM_PADDING
		
		# NOTE: Need special first delegate -- here? Or probably just deal with it
		# on layout changes
		self._delegate_provider  = delegate_lookup.BSDelegateProvider(view=self)
	
		self.applyHeaderConstraints()

		self.header().sectionCountChanged.connect(self._delegate_provider.refreshDelegates)

	def syncFromHeader(self, header:QtWidgets.QHeaderView):
		"""Sync header from another header"""

		self.header().restoreState(
			header.saveState()
		)

		self._delegate_provider.refreshDelegates()

		# Add additional padding to first-column delegate
		first_col_logical = self.header().logicalIndex(0)
		first_col_width   = self.header().sectionSize(first_col_logical)

		new_del = self._delegate_provider.delegateForColumn(
			first_col_logical,
			unique_instance=True
		)

		# How much more padding to add
		addtl_padding = self.frameRect().right() + self._item_padding.right()

		new_padding = QtCore.QMarginsF(self._item_padding)
		
		new_padding.setLeft(self._item_padding.left() + addtl_padding)
		new_padding.setBottom(max(
			self.frameRect().height(),
			self._item_padding.bottom()
		))
		new_del.setItemPadding(new_padding)

		self._delegate_provider.setDelegateForColumn(first_col_logical, new_del)
		
		self.header().resizeSection(
			first_col_logical,
			first_col_width + self.frameRect().right() + self._item_padding.right()
		)

		self.applyHeaderConstraints()
	
	def delegateProvider(self) -> delegate_lookup.BSDelegateProvider:

		return self._delegate_provider

	@QtCore.Slot(object)
	def setFrameScale(self, frame_scale:float):
		
		if frame_scale == self._frame_scale:
			return
		
		self._frame_scale = frame_scale
		
		#self._delegate_provider.refreshDelegates()
		self.refreshDelegatePadding()

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
			return
		
		self._item_padding = padding
		
		self.refreshDelegatePadding()
		
		self.sig_item_padding_changed.emit(padding)

	def refreshDelegatePadding(self):
		"""Re-calculate and re-apply padding data when size stuff changes"""

		script_pad = QtCore.QMarginsF(self._item_padding)
		old_pad = QtCore.QMarginsF(script_pad)
		script_pad.setBottom(max(
			self.frameRect().height(),
			self._item_padding.bottom()

		))

#		script_pad.setLeft(self.frameRect().width() + script_pad.left() + script_pad.right())

		#print(f"{old_pad=} {script_pad=}")

		first_section_logical = self.header().logicalIndex(0)

		for col in range(self.header().count()):

			if col == first_section_logical:
				first_pad = QtCore.QMarginsF(script_pad)
				first_pad.setLeft(self.frameRect().width() + script_pad.left() + script_pad.right())
				self._delegate_provider.delegateForColumn(col).setItemPadding(first_pad)

				self.resizeColumnToContents(col)
			else:
				self._delegate_provider.delegateForColumn(col).setItemPadding(script_pad)

	def applyHeaderConstraints(self):
		"""Header constraints"""

		# Since I copy header from list view to script view, need to restore a lot of constraints

		self.header().setSectionsMovable(False)
		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		self.setSortingEnabled(False)
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.SingleSelection)
		self.setDragEnabled(True)

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
				frame_rect.right() + self._item_padding.left(),
				options.rect.bottom() - item_delegate.itemPadding().bottom() + item_delegate.itemPadding().top(),
			),

			QtCore.QPointF(
				options.rect.right() - item_delegate.itemPadding().right(),
				frame_rect.bottom()
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