from PySide6 import QtCore, QtGui, QtWidgets
from ..listview import treeview, binitems
import avbutils

class BSBinScriptView(treeview.BSBinTreeView):
	"""Script view"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frame_size = QtCore.QSizeF(16, 9).scaled(QtCore.QSizeF(*[100]*2), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
		
		#self.setAlternatingRowColors(False)
		
		self.applyHeaderConstraints()


	def applyHeaderConstraints(self):
		"""Header constraints"""

		# These need to be re-applied after restoringState to sync with other views

#		for col in range(self.header().count()):
#
#			delegate = self.itemDelegateForColumn(col)
#			padding  = delegate.itemPadding()
#			padding  = QtCore.QMargins(padding.left(), padding.top(), padding.right(), padding.bottom() + 40)
#		#	delegate.setItemPadding(padding)


		#old_del  = self.itemDelegateForColumn(0)
		#margins = old_del.itemPadding()
		
		# NOTE: 200 conrtols width(?), 112 def controls height of row
		delegate = binitems.BSGenericItemDelegate(QtCore.QMargins(self._frame_size.width() + 16,0,0,self._frame_size.height()))
		self.setItemDelegateForColumn(self.header().logicalIndex(0),delegate)

		# Resize first section to accomodate frame
		self.header().resizeSection(self.header().logicalIndex(0), self.header().sectionSize(self.header().logicalIndex(0)) + self._frame_size.width() + 16)


		self.header().setSectionsMovable(False)
		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		#self.header().set
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.SingleSelection)
		self.setSortingEnabled(False)
		self.setDragEnabled(True)

	def rowsInserted(self, parent:QtCore.QModelIndex, start:int, end:int):
		
		for row in range(start, end+1):
			
			idx_row = self.model().index(row, 0, parent)
			delegate = self.itemDelegate(idx_row)
			delegate = delegate.__class__(delegate)
		#	delegate.setItemPadding(QtCore.QMargins(5,5, 5, 500))		

		#	self.setItemDelegateForColumn(0, delegate)	

	def drawRow(self, painter:QtGui.QPainter, options:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
		
		options = QtWidgets.QStyleOptionViewItem(options)
		
		super().drawRow(painter, options, index)
		return

		if options.state & QtWidgets.QStyle.StateFlag.State_Selected:
			print([s for s in options.state])
			brush = options.palette.highlight()
			pen = QtGui.QPen(options.palette.windowText().color())
			pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
			painter.setBrush(brush)
			painter.setPen(pen)
			painter.drawRect(options.rect)
			
		else:
			print(options.features)
			brush = options.palette.base()
			#pen = QtGui.QPen(options.palette.windowText().color())
			#pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
			painter.setBrush(brush)
			painter.setPen(QtGui.QPen())
			painter.drawRect(options.rect)
		self.viewport().update(options.rect)
			


		
		return
		
		list_rect         = QtCore.QRect(options.rect)
		list_rect.setHeight(32)

		list_options      = QtWidgets.QStyleOptionViewItem(options)
		list_options.rect = list_rect
		list_options.backgroundBrush = QtGui.QBrush()



		painter.save()

		DEFAULT_PADDING = QtCore.QMarginsF(8,8,8,8)

		frame_rect = QtCore.QRectF(
			QtCore.QPointF(
				options.rect.left() + DEFAULT_PADDING.left(),
				options.rect.top() + DEFAULT_PADDING.top(),
			),
			self._frame_size
		)



		fields = index.model().sourceModel().fields()
		field_index = fields.index(str(avbutils.BIN_COLUMN_ROLES["Name"]))
		#print(fields, field_index)

		src_index = index.model().mapToSource(index)


		script_text = src_index.siblingAtColumn(field_index).data(QtCore.Qt.ItemDataRole.DisplayRole)

		script_rect = QtCore.QRectF(
			QtCore.QPointF(
				frame_rect.right() + DEFAULT_PADDING.left(),
				list_rect.bottom(),
			),

			QtCore.QPointF(
				options.rect.right() - DEFAULT_PADDING.right(),
				frame_rect.bottom(),
			)
		)

		pen = QtGui.QPen()
		pen.setColor(options.palette.windowText().color())
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

		brush = QtGui.QBrush()
		brush.setColor(options.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRect(script_rect)
		painter.drawText(script_rect, script_text)

		painter.drawRect(frame_rect)

		painter.restore()

		self.viewport().update(options.rect) # NOTE: Not just active_rect -- Scrolling needs to repaint the whole thing