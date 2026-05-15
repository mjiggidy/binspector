from __future__ import annotations
import typing

from PySide6 import QtWidgets, QtGui, QtCore

from . import editorproxymodel
from ..binview import binviewitemtypes

if typing.TYPE_CHECKING:
	from . import editorwidget

class BSBinViewColumnDelegate(QtWidgets.QStyledItemDelegate):

	sig_hide_column_index       = QtCore.Signal(QtCore.QModelIndex)
	sig_remove_column_index     = QtCore.Signal(QtCore.QModelIndex)
	sig_rename_column_for_index = QtCore.Signal(QtCore.QModelIndex, str)


	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		# NOTE: This gets confusing
		# The column editor view model returns the bin view column view item from its UserRole
		# which isn't even clear as I write it here. lol TODO: Refactor
		
		#item:viewmodelitems.LBAbstractViewHeaderItem = index.data(QtCore.Qt.ItemDataRole.UserRole)
		editor_feature = index.model().headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
		
		is_hidden = index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

		#option.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus

		# Show hidden as dimmed
		if is_hidden:
			option.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled

			font = QtGui.QFont(option.font)
			font.setItalic(True)
			option.font = font
			option.fontmetrics = QtGui.QFontMetrics(font)
			
		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn and option.state & QtWidgets.QStyle.StateFlag.State_HasFocus:
			option.palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Active)
		
		super().paint(painter, option, index)

	def editorEvent(self, event:QtCore.QEvent, model:QtCore.QAbstractItemModel, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> bool:

		print("delegate editorEvent got index ", index)

		editor_feature = model.headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		self.initStyleOption(option, index)

		if not event.type() == QtCore.QEvent.Type.MouseButtonRelease:
			return False

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:  # TODO: Use checked State?

			self.sig_hide_column_index.emit(index)
			return True
		
		elif editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn and model.userCanDelete(index):
#			print("Delegate says remove ", index.siblingAtColumn(0).data(QtCore.Qt.ItemDataRole.DisplayRole))
			self.sig_remove_column_index.emit(index)
			return True

		return False

	
	def setModelData(self, editor:QtWidgets.QWidget, model:QtCore.QAbstractItemModel, index:QtCore.QModelIndex):
		
		editor_feature = model.headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:

			column_name = editor.text()
			self.sig_rename_column_for_index.emit(index, column_name)
	
	def setEditorData(self, editor:QtWidgets.QLineEdit, index:QtCore.QModelIndex):
		
		editor_feature = index.model().headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
			column_name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
			editor.setText(column_name)