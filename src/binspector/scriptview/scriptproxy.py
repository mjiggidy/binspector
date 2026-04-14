from PySide6 import QtCore
import avbutils

from ..binitems import binitemtypes
from ..binview  import binviewitemtypes


class BSScriptViewProxyModel(QtCore.QAbstractProxyModel):
	"""Because of the frame thing.  You know."""

	ADDITIONAL_COLUMNS = 1
	DEFAULT_ITEM_FLAGS = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled

	def __init__(self, /, parent:QtCore.QObject):

		super().__init__(parent)

		self._additional_header = binviewitemtypes.BSBinViewColumnInfo(
			field_id     = avbutils.bins.BinColumnFieldIDs.Frame,
			format_id    = avbutils.bins.BinColumnFormat.Frame,
			display_name = "",
			is_hidden    = False
		)

	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		return QtCore.QModelIndex()

	def columnCount(self, /, parent:QtCore.QModelIndex):

		if parent.isValid() or not self.sourceModel():
			return 0

		return self.sourceModel().columnCount(QtCore.QModelIndex()) + self.ADDITIONAL_COLUMNS
	
	def rowCount(self, /, parent:QtCore.QModelIndex):

		if parent.isValid() or not self.sourceModel():
			return 0

		return self.sourceModel().rowCount(QtCore.QModelIndex())
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex):

		# NOTE TO SELF: Surprised this needs to be reimplemented...?

		if parent.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		if not proxyIndex.isValid() or not self.sourceModel():
			return None

		if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtCore.Qt.AlignmentFlag.AlignTop
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			
			# Return any of my special lil' binitemtypes
			if int(role) > int(QtCore.Qt.ItemDataRole.UserRole):	
				return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(role)
			else:
				return None

		return self.mapToSource(proxyIndex).data(role)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole):
		
		if not self.sourceModel() or orientation != QtCore.Qt.Orientation.Horizontal:
			return None
		
		if section < self.ADDITIONAL_COLUMNS:
			return self._additional_header.data(role)
		
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