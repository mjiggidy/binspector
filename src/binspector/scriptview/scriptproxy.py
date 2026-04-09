from PySide6 import QtCore
from ..binitems import binitemtypes
from ..binview import binviewitemtypes

class BSScriptViewProxyModel(QtCore.QIdentityProxyModel):
	"""Because of the frame thing.  You know."""

	ADDITIONAL_COLUMNS = 1
	DEFAULT_ITEM_FLAGS = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled

	def columnCount(self, /, parent:QtCore.QModelIndex):

		if parent.isValid() or not self.sourceModel():
			return 0

		return self.sourceModel().columnCount(QtCore.QModelIndex()) + self.ADDITIONAL_COLUMNS
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex):

		# NOTE TO SELF: Surprised this needs to be reimplemented...?

		if parent.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column, None)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		if not proxyIndex.isValid() or not self.sourceModel():
			return None
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return str(self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(binitemtypes.BSBinItemDataRoles.FrameThumbnailRole))

		return self.mapToSource(proxyIndex).data(role)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole):
		
		if not self.sourceModel():
			return None
		
		if section < self.ADDITIONAL_COLUMNS:
			return "Thumbnail"
		
		return self.sourceModel().headerData(section - self.ADDITIONAL_COLUMNS, orientation, role)
	
	def flags(self, proxyIndex:QtCore.QModelIndex):

		if not proxyIndex.isValid() or not self.sourceModel():
			return QtCore.Qt.ItemFlag.NoItemFlags
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			return self.DEFAULT_ITEM_FLAGS
		
		return self.mapToSource(proxyIndex).flags()
		
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if not sourceIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()

		return self.index(sourceIndex.row(), sourceIndex.column() + self.ADDITIONAL_COLUMNS, QtCore.QModelIndex())
	
	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if not proxyIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			return QtCore.QModelIndex()
		
		return self.sourceModel().index(proxyIndex.row(), proxyIndex.column() - self.ADDITIONAL_COLUMNS, QtCore.QModelIndex())