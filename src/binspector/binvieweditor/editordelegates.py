from __future__ import annotations
import typing

from PySide6 import QtWidgets, QtGui, QtCore

from . import editorproxymodel
from ..binview import binviewitemtypes
import avbutils

if typing.TYPE_CHECKING:
	from . import editorwidget

class BSBinViewColumnDelegate(QtWidgets.QStyledItemDelegate):

	sig_hide_column_index       = QtCore.Signal(int, QtCore.QModelIndex)
	sig_remove_column_index     = QtCore.Signal(int, QtCore.QModelIndex)
	sig_rename_column_for_index = QtCore.Signal(int, QtCore.QModelIndex, str)


	def paint(self, painter:QtGui.QPainter, option_item:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		self.initStyleOption(option_item, index)
#		print(option_item.state)

		view_widget:QtWidgets.QAbstractItemView = option_item.widget
		editor_feature = index.model().headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		
		is_hidden = index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

		#option.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus

		# Show hidden as dimmed
		if is_hidden:

			option_item.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled

			font = QtGui.QFont(option_item.font)
			font.setItalic(True)
			option_item.font = font
			option_item.fontmetrics = QtGui.QFontMetrics(font)
			
#		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn and option.state & QtWidgets.QStyle.StateFlag.State_HasFocus:
#			option.palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Active)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:

			#min_size = min(option_item.rect.width(), option_item.rect.height())
			button_rect = QtCore.QRect(option_item.rect)
			button_rect = button_rect.marginsRemoved(QtCore.QMargins(1,1,1,1))


			button_option = QtWidgets.QStyleOptionButton()
			button_option.rect = button_rect
			button_option.icon = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
			button_option.iconSize = QtCore.QSize(*[view_widget.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)*.75]*2)
			button_option.state = option_item.state

			if all((
				option_item.state & QtWidgets.QStyle.StateFlag.State_Selected,
				QtWidgets.QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton,
				view_widget.currentIndex().column() == index.column()
			)):
				button_option.state |= QtWidgets.QStyle.StateFlag.State_Sunken
			
			style = option_item.widget.style()
			style.drawControl(QtWidgets.QStyle.ControlElement.CE_PushButton, button_option, painter)

		elif editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn:

			is_deletable = index.data(QtCore.Qt.ItemDataRole.UserRole)

			if not is_deletable:
				
				super().paint(painter, option_item, index)
				return
			
			button_rect = QtCore.QRect(option_item.rect)
			button_rect = button_rect.marginsRemoved(QtCore.QMargins(1,1,1,1))

			button_option = QtWidgets.QStyleOptionButton()
			button_option.rect = button_rect
			button_option.icon = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
			button_option.iconSize = QtCore.QSize(*[view_widget.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)*.75]*2)
			button_option.state = option_item.state

			if all((
				option_item.state & QtWidgets.QStyle.StateFlag.State_Selected,
				QtWidgets.QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton,
				view_widget.currentIndex().column() == index.column()
			)):
#				print(view_widget.currentIndex().column() == index.column())
				button_option.state |= QtWidgets.QStyle.StateFlag.State_Sunken

			style = option_item.widget.style()
			style.drawControl(QtWidgets.QStyle.ControlElement.CE_PushButton, button_option, painter)


		else:
		
			super().paint(painter, option_item, index)

	def editorEvent(self, event:QtCore.QEvent, model:QtCore.QAbstractItemModel, option_item:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> bool:

		if event.type() not in (QtCore.QEvent.Type.MouseButtonRelease, QtCore.QEvent.Type.MouseButtonPress, QtCore.QEvent.Type.MouseButtonRelease):
			return False
		
		# NOTE: Boy this was awful.  The index gets mappedFromSource so the column always = 0
		# Need to ask the view instead I guess...?
		
		view_widget:QtWidgets.QAbstractItemView = option_item.widget
		actual_index   = view_widget.indexAt(event.pos())
		editor_feature = model.headerData(actual_index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

#		print("delegate editorEvent got index ", actual_index)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:  # TODO: Use checked State?

			if event.type() == QtCore.QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton:
				

				for selected_button_index in view_widget.selectionModel().selectedRows(actual_index.column()):
					view_widget.update(selected_button_index)
				

			elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.LeftButton:

				#view_widget.update(actual_index)
				for selected_button_index in view_widget.selectionModel().selectedRows(actual_index.column()):

					if selected_button_index.data(QtCore.Qt.ItemDataRole.UserRole):
						self.sig_hide_column_index.emit(selected_button_index.row(), QtCore.QModelIndex())

					view_widget.update(selected_button_index)

			#return True
		
		elif editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn:
			
#			print("User clicked delete col")

			if event.type() == QtCore.QEvent.Type.MouseButtonPress and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
		
				view_widget.update(actual_index)
			
			elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
				
				if actual_index.data(QtCore.Qt.ItemDataRole.UserRole):
					
					self.sig_remove_column_index.emit(actual_index.row(), QtCore.QModelIndex())

				view_widget.update(actual_index)

			#return True

		return super().editorEvent(event, model, option_item, index)
	
	def sizeHint(self, option, index):
		return super().sizeHint(option, index)

	
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