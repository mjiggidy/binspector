
import typing
from PySide6 import QtCore
from avbutils import bins

from . import binitemtypes

type BSBinItemModelEntry = dict[bins.BinColumnFieldIDs, binitemtypes.BSAbstractViewItem]
"""Each bin item in the model is a dict of BinColumnFieldID and respective view item pairs"""

class BSBinItemModel(QtCore.QAbstractItemModel):
	"""Single-column item model for bin items"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._bin_items:list[BSBinItemModelEntry] = []

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Number of bin items"""
		
		return 0 if parent.isValid() else len(self._bin_items)

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Column count for model (returns `1` for flat model)"""

		return 0 if parent.isValid() else 1
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		"""Model is flat and has no children"""
		
		return not parent.isValid()
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Model is flat, children have no parents"""
		
		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		if column > self.columnCount(parent):
			return QtCore.QModelIndex()
		
		if row > self.rowCount(self.parent):
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:binitemtypes.BSBinItemDataRoles) -> typing.Any:
		
		if not index.isValid():
			return None
		
		bin_item = self._bin_items[index.row()]
		
		# Map BinItemDataRoles to their avbutils counterparts
		if role == binitemtypes.BSBinItemDataRoles.ItemNameRole:
			return bin_item.get(bins.BinColumnFieldIDs.Name).raw_data()
		
		elif role == binitemtypes.BSBinItemDataRoles.FrameCoordinatesRole:
			# NOTE: TODO
			return [100,100]
		
		elif role == binitemtypes.BSBinItemDataRoles.ClipColorRole:
			return bin_item.get(bins.BinColumnFieldIDs.Color).raw_data()
		
		elif role == binitemtypes.BSBinItemDataRoles.ItemTypesRole:
			return bin_item.get(bins.BinColumnFieldIDs.BinItemIcon).raw_data()
		
		elif role == binitemtypes.BSBinItemDataRoles.ScriptNotesRole:
			return self._getUserColumnItem(index, user_column_name="Comments", role=QtCore.Qt.ItemDataRole.DisplayRole)