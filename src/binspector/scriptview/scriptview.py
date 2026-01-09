from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSScriptViewConfig

from . import delegates
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
		self._delegate_provider     = delegate_lookup.BSDelegateProvider(view=self)
		self._delegate_script_notes = delegates.BSScriptNotesDelegate(parent=self)
	
		self.applyHeaderConstraints()

		self.header().sectionCountChanged.connect(self._delegate_provider.refreshDelegates)

	def syncFromHeader(self, header:QtWidgets.QHeaderView):
		"""Sync header from another header"""

		self.header().restoreState(
			header.saveState()
		)

		self.refreshDelegates()
		self.applyHeaderConstraints()
	
	def delegateProvider(self) -> delegate_lookup.BSDelegateProvider:

		return self._delegate_provider

	@QtCore.Slot(object)
	def setFrameScale(self, frame_scale:float):
		
		if frame_scale == self._frame_scale:
			return
		
		self._frame_scale = frame_scale
		
		self.refreshDelegates()

		# Re-draw drawRow()
		self.viewport().update()

		self.sig_frame_scale_changed.emit(frame_scale)

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
		
		self.refreshDelegates()
		
		self.sig_item_padding_changed.emit(padding)

	def _firstItemOffset(self) -> float:

		return self._item_padding.left() + self.frameRect().width() + self._item_padding.right()

	def adjustFirstItemPadding(self):
		"""Adjust the first item delegate's padding to make room for frame stuff"""

		first_col_logical = self.header().logicalIndex(0)

		
		first_col_width   = self.header().sectionSize(first_col_logical)

		new_del = self._delegate_provider.delegateForColumn(
			first_col_logical,
			unique_instance=True
		)

		# How much more padding to add
		addtl_padding = self._firstItemOffset()

		new_padding = QtCore.QMarginsF(self._item_padding)
		
		new_padding.setLeft(addtl_padding)
		new_padding.setBottom(max(
			self.frameRect().height(),
			self._item_padding.bottom()
		))
		new_del.setItemPadding(new_padding)

		self._delegate_provider.setDelegateForColumn(first_col_logical, new_del)
		
		self.header().resizeSection(
			first_col_logical,
			first_col_width + addtl_padding
		)

		print(f"Adjust from {first_col_width=} to {first_col_width + addtl_padding =}")

	def refreshDelegates(self):
		"""Re-calculate and re-apply padding data when size stuff changes"""

		script_item_padding = QtCore.QMarginsF(self._item_padding)
		
		# Add bottom padding for at least the frame rect
		script_item_padding.setBottom(max(
			self.frameRect().height(),
			self._item_padding.bottom()
		))
#		)

		done_dels = set()
		
		self._delegate_provider.defaultItemDelegate().setItemPadding(script_item_padding)

		done_dels.add(self._delegate_provider.defaultItemDelegate())

		for col in range(self.header().count()):
			
			new_del = self._delegate_provider.delegateForColumn(col)
			
			if new_del not in done_dels:
				new_del.setItemPadding(script_item_padding)
				done_dels.add(new_del)
			
			self._delegate_provider.setDelegateForColumn(col, new_del)

		#self.adjustFirstItemPadding()

	def applyHeaderConstraints(self):
		"""Header constraints"""

		# Since I copy header from list view to script view, need to restore a lot of constraints

		self.header().setSectionsMovable(False)
		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		self.setSortingEnabled(False)
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.SingleSelection)
		self.setDragEnabled(True)

	def drawRow(self, painter:QtGui.QPainter, options:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
		
		item_delegate = self.itemDelegate(index)

		super().drawRow(painter, options, index)

		frame_rect = self.frameRect().translated(
			QtCore.QPointF(
				options.rect.left() + self._item_padding.left(),
				options.rect.top()  +self._item_padding.top(),
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

		from ..models import viewmodelitems
		# NOTE: Getting "None" here.
		script_text = index.data(role=viewmodelitems.BSBinItemDataRoles.BSScriptNotes)

		print(options.state)
		pen = QtGui.QPen()
		pen.setColor(
			options.palette.highlightedText().color() \
			  if options.state & QtWidgets.QStyle.StateFlag.State_Item \
			  else options.palette.windowText().color()
		)
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

		brush = QtGui.QBrush()
		brush.setColor(options.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.save()
		
		painter.setPen(pen)
		painter.setBrush(brush)

		script_note_options = QtWidgets.QStyleOptionViewItem(options)
		script_note_options.rect = script_rect.toRect()
		script_note_options.text = index.data(role=viewmodelitems.BSBinItemDataRoles.BSScriptNotes)
		self._delegate_script_notes.paint(painter, script_note_options, index)

#		painter.drawRect(script_rect)
#		painter.drawText(script_rect, script_text)

		painter.drawRect(frame_rect)

		painter.restore()