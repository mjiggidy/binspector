from __future__ import annotations
import typing

from PySide6 import QtWidgets, QtGui, QtCore
from ..models import viewmodelitems
from . import editorproxymodel

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
		role =index.model().featureForIndex(index)
		
		is_hidden = index.data(viewmodelitems.BSBinColumnDataRoles.BSColumnIsHidden)

		#option.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus

		# Show hidden as dimmed
		if is_hidden:
			option.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled

			font = QtGui.QFont(option.font)
			font.setItalic(True)
			option.font = font
			option.fontmetrics = QtGui.QFontMetrics(font)
			
		if role == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn and option.state & QtWidgets.QStyle.StateFlag.State_HasFocus:
			option.palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Active)
		
		super().paint(painter, option, index)

	def editorEvent(self, event:QtCore.QEvent, model:editorproxymodel.BSBinViewColumnEditorProxyModel, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> bool:

		#print(model.featureForIndex(index))

		role = model.featureForIndex(index)

		if not event.type() == QtCore.QEvent.Type.MouseButtonRelease:
			return False

		if role == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:  # TODO: Use checked State?

			self.sig_hide_column_index.emit(index)
			return True
		
		elif role == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn and model.userCanDelete(index):
			print("Delegate says remove ", index.siblingAtColumn(0).data(QtCore.Qt.ItemDataRole.DisplayRole))
			self.sig_remove_column_index.emit(index)

		return False

	
	def setModelData(self, editor:QtWidgets.QWidget, model:editorproxymodel.BSBinViewColumnEditorProxyModel, index:QtCore.QModelIndex):
		
		role = model.featureForIndex(index)

		if role == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:

			column_name = editor.text()
			self.sig_rename_column_for_index.emit(index, column_name)
	
	def setEditorData(self, editor:QtWidgets.QLineEdit, index:QtCore.QModelIndex):
		
		role = index.model().featureForIndex(index)

		if role == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
			column_name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
			editor.setText(column_name)