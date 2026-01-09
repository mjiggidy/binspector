"""
Item Delegates specifically for Script View
"""

from PySide6 import QtCore, QtGui, QtWidgets

class BSScriptNotesDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter, option, index):
		
		self.initStyleOption(option, index)

		script_notes_rect = QtCore.QRectF(option.rect)

		pen = QtGui.QPen()
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setWidthF(1/painter.device().devicePixelRatioF())
		pen.setColor(
			option.palette.highlightedText().color() \
			  if option.state & QtWidgets.QStyle.StateFlag.State_Item \
			  else option.palette.windowText().color()
		)

		brush = QtGui.QBrush()
		brush.setColor(option.palette.window().color())
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.save()
		
		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRect(script_notes_rect)
		painter.drawText(script_notes_rect, option.text)

		painter.restore()