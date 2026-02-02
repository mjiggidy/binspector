from __future__ import annotations
import typing

from PySide6 import QtWidgets, QtGui, QtCore
from ..models import viewmodelitems
from . import editorproxymodel

if typing.TYPE_CHECKING:
	from . import editorwidget

class BSBinViewColumnDelegate(QtWidgets.QStyledItemDelegate):


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

		if role == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn and option.state & QtWidgets.QStyle.StateFlag.State_HasFocus:
			option.palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Active)
		
		super().paint(painter, option, index)

	def editorEvent(self, event:QtCore.QEvent, model:editorproxymodel.BSBinViewColumnEditorProxyModel, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> bool:

		print(model.featureForIndex(index))

		role = model.featureForIndex(index)

		if role == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:  # TODO: Use checked State?


			if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
				is_hidden = not index.data(viewmodelitems.BSBinColumnDataRoles.BSColumnIsHidden)
				model.setData(index, is_hidden, viewmodelitems.BSBinColumnDataRoles.BSColumnIsHidden)

			return True
		
		return False

	
	def setModelData(self, editor:QtWidgets.QWidget, model:editorproxymodel.BSBinViewColumnEditorProxyModel, index:QtCore.QModelIndex):
		
		role = model.featureForIndex(index)

		if role == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:

			column_name = editor.text()
			model.setData(index, column_name, viewmodelitems.BSBinColumnDataRoles.BSColumnDisplayName)

		return super().setModelData(editor, model, index)
	
	def setEditorData(self, editor:QtWidgets.QLineEdit, index:QtCore.QModelIndex):
		
		role = index.model().featureForIndex(index)

		if role == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
			column_name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
			editor.setText(column_name)