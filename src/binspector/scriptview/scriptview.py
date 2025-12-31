from PySide6 import QtCore, QtGui, QtWidgets
from ..listview import treeview
import avbutils

class BSBinScriptView(treeview.BSBinTreeView):
	"""Script view"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self.setUniformRowHeights(False)

		#self.setAlternatingRowColors(False)

	# NOTE: Need additional proxy for manual moving/sorting/positions?

	def rowsInserted(self, parent:QtCore.QModelIndex, start:int, end:int):
		
		for row in range(start, end+1):
			
			idx_row = self.model().index(row, 0, parent)
			delegate = self.itemDelegate(idx_row)
			delegate = delegate.__class__(delegate)
			delegate.setItemPadding(QtCore.QMargins(5,5, 5, 300))		

			self.setItemDelegateForColumn(0, delegate)	

	def drawRow(self, painter:QtGui.QPainter, options:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		usual_rect = options.rect.adjusted(0, 0, 0, -options.rect.height()/2)
		new_options = QtWidgets.QStyleOptionViewItem(options)
		new_options.rect = usual_rect
		super().drawRow(painter, new_options, index)

		painter.save()

		fields = index.model().sourceModel().fields()
		field_index = fields.index(str(avbutils.BIN_COLUMN_ROLES["Name"]))
		#print(fields, field_index)

		src_index = index.model().mapToSource(index)


		text = src_index.siblingAtColumn(field_index).data(QtCore.Qt.ItemDataRole.DisplayRole)

		active_rect = QtCore.QRectF(options.rect)
		active_rect = active_rect.marginsRemoved(QtCore.QMarginsF(32, options.rect.height()/2, 8, 8))

		pen = QtGui.QPen()
		pen.setColor(options.palette.windowText().color())
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

		brush = QtGui.QBrush()
		brush.setColor(options.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRect(active_rect)
		painter.drawText(active_rect, text)

		painter.restore()

		self.viewport().update(options.rect) # NOTE: Not just active_rect -- Scrolling needs to repaint the whole thing