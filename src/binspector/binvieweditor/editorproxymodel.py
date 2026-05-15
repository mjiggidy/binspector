import enum

from ..binview import binviewitemtypes
from PySide6 import QtCore, QtGui

import avbutils

class BSBinViewColumnEditorFeature(enum.IntEnum):
	"""Editor column features"""

	GripperColumn     = enum.auto()
	NameColumn        = enum.auto()
	DataFormatColumn  = enum.auto()
	VisibilityColumn  = enum.auto()
	DeleteColumn      = enum.auto()

class BSBinViewColumnEditorProxyModel(QtCore.QAbstractProxyModel):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._editor_features:list[BSBinViewColumnEditorFeature] = [
			BSBinViewColumnEditorFeature.DataFormatColumn,
			BSBinViewColumnEditorFeature.NameColumn,
			BSBinViewColumnEditorFeature.DeleteColumn,
			BSBinViewColumnEditorFeature.VisibilityColumn,
		]

	###

	def setSourceModel(self, sourceModel:QtCore.QAbstractItemModel):
		
		if self.sourceModel() == sourceModel:
			return
		
		if self.sourceModel():
			self.sourceModel().disconnect(self)

		sourceModel.rowsAboutToBeRemoved.connect(self.sourceModelAboutToRemoveRows)
		sourceModel.rowsRemoved.connect(self.sourceModelRemovedRows)

		sourceModel.rowsAboutToBeInserted.connect(self.sourceModelAboutToInsertRows)
		sourceModel.rowsInserted.connect(self.sourceModelInsertedRows)

		sourceModel.rowsAboutToBeMoved.connect(self.sourceModelAboutToMoveRows)
		sourceModel.rowsMoved.connect(self.sourceModelMovedRows)

		sourceModel.modelAboutToBeReset.connect(self.modelAboutToBeReset)
		sourceModel.modelReset.connect(self.modelReset)

		sourceModel.layoutChanged.connect(self.layoutChanged)
		sourceModel.dataChanged.connect(self.sourceModelDataChanged)
		
		super().setSourceModel(sourceModel)

		print("Source set", sourceModel)

	### Source Model Malarky

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelAboutToRemoveRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if parent.isValid():
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), row_start, row_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelRemovedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if parent.isValid():
			return
		
		self.endRemoveRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelAboutToInsertRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):
		
		if parent.isValid():
			return
		
		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelInsertedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if parent.isValid():
			return
		
		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceModelAboutToMoveRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int, destination:QtCore.QModelIndex, dest_row:int):

		if parent.isValid():
			return

		self.beginMoveRows(QtCore.QModelIndex(), row_start, row_end, QtCore.QModelIndex(), dest_row)

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceModelMovedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int, destination:QtCore.QModelIndex, dest_row:int):

		if parent.isValid():
			return

		self.endMoveRows()

	@QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex, list)
	def sourceModelDataChanged(self, topLeft:QtCore.QModelIndex, bottomRight:QtCore.QModelIndex, roles:list[QtCore.Qt.ItemDataRole]):

		self.dataChanged.emit(
			self.index(topLeft.row(), 0, QtCore.QModelIndex()),
			self.index(bottomRight.row(), self.columnCount(QtCore.QModelIndex()) - 1, QtCore.QModelIndex())
		)

	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if not proxyIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex())
	
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if not sourceIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.index(sourceIndex.row(), 0, QtCore.QModelIndex())

	### Model Malarky

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 0 if parent.isValid() else len(self._editor_features)
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if not self.sourceModel() or parent.isValid():
			return 0
		
		return self.sourceModel().rowCount(QtCore.QModelIndex())
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		return False
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex):

		if parent.isValid():
			return QtCore.QModelIndex()
		
#		print(f"Proxy creating index for: {row=}, {column=}")
		
		return self.createIndex(row, column)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		editor_feature = self._editor_features[proxyIndex.column()]

		if editor_feature == BSBinViewColumnEditorFeature.DataFormatColumn:
			
			data_format:avbutils.bins.BinColumnFormat = self.mapToSource(proxyIndex).data(binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return data_format.name[0].upper()
			
			elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
				return self.tr("<strong>Column Data Format</strong><br/>{data_format_name}").format(data_format_name = data_format.name.title())
			
		elif editor_feature == BSBinViewColumnEditorFeature.VisibilityColumn:

			is_hidden = self.mapToSource(proxyIndex).data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

			if role == QtCore.Qt.ItemDataRole.DecorationRole:
				return QtGui.QIcon(":/icons/gui/toggle_visibilty_off.svg") if is_hidden else  QtGui.QIcon(":/icons/gui/toggle_visibilty_on.svg")
			if role == QtCore.Qt.ItemDataRole.ToolTipRole:
				return self.tr("<strong>Toggle Column Visibility</strong><br/>This column is currently {is_hidden}").format(is_hidden = self.tr("hidden", "Referring to column visibility") if is_hidden else self.tr("visible",  "Referring to column visibility"))

			
		elif editor_feature == BSBinViewColumnEditorFeature.DeleteColumn:

			is_deletable = self._columnCanBeDeletedIsThatCorrectPlease(
				self.mapToSource(proxyIndex).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
			)

			if role == QtCore.Qt.ItemDataRole.DecorationRole:
				
				# Allow delete if user field
				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove) if is_deletable else QtGui.QIcon()

		else:
			return self.mapToSource(proxyIndex).data(role)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole):

		if orientation != QtCore.Qt.Orientation.Horizontal:
			return
		
		editor_feature = self._editor_features[section]

		if role == QtCore.Qt.ItemDataRole.UserRole:
			return editor_feature
		
#		if role == QtCore.Qt.ItemDataRole.DisplayRole:
#			return editor_feature.name
	
	def flags(self, index:QtCore.QModelIndex):
		
#		editor_feature = self._editor_features[index.column()]
		
		flags = \
			QtCore.Qt.ItemFlag.ItemIsEnabled | \
			QtCore.Qt.ItemFlag.ItemIsSelectable | \
			QtCore.Qt.ItemFlag.ItemNeverHasChildren

		# Allow dropping between items (invalid indexes)
		if not index.isValid():
			return QtCore.Qt.ItemFlag.ItemIsDropEnabled
		
		# Column Name Edididable if user field and we're talkin bout the name column here
#		if editor_feature == BSBinViewColumnEditorFeature.NameColumn \
#		   and self.mapToSource(index).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User:
#			flags |= QtCore.Qt.ItemFlag.ItemIsEditable
		
		return flags | QtCore.Qt.ItemFlag.ItemIsDragEnabled
	
	### Draggityy Droppity Mimeity businesses

	def supportedDragActions(self) -> QtCore.Qt.DropAction:
		return QtCore.Qt.DropAction.MoveAction
	
	def supportedDropActions(self)-> QtCore.Qt.DropAction:
		return QtCore.Qt.DropAction.MoveAction
	
	def mimeTypes(self):
		return ["application/x-qabstractitemmodeldatalist"]
	
	def canDropMimeData(self, data:QtCore.QMimeData, action:QtCore.Qt.DropAction, row:int, column:int, parent:QtCore.QModelIndex):
		# Only allow drops *between* items
		# (Pairs with flags() returning ItemFalgs.ItemAcceptsDrops for invalid QModelIndexes)
		return not parent.isValid()

	def moveRows(self, sourceParent:QtCore.QModelIndex, sourceRow:int, count:int, destinationParent:QtCore.QModelIndex, destinationChild:int):

		self.sourceModel().moveRows(
			QtCore.QModelIndex(),
			sourceRow,
			count,
			QtCore.QModelIndex(),
			destinationChild
		)
		
		return super().moveRows(sourceParent, sourceRow, count, destinationParent, destinationChild)
	
	def dropMimeData(self, data:QtCore.QMimeData, action:QtCore.Qt.DropAction, row:int, column:int, parent:QtCore.QModelIndex) -> bool:

		if action == QtCore.Qt.DropAction.MoveAction and data.hasFormat("application/x-qabstractitemmodeldatalist"):
			return True

		return super().dropMimeData(data, action, row, column, parent)
	
	### Helper junk

	def _columnCanBeDeletedIsThatCorrectPlease(self, field_id:avbutils.bins.BinColumnFieldIDs) -> bool:

		return field_id == avbutils.bins.BinColumnFieldIDs.User