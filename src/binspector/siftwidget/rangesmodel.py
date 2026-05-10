import typing, dataclasses
from PySide6 import QtCore
import avbutils

from ..binview import binviewitemtypes
from ..binitems import binitemtypes
from ..binfilters.siftfilter.sifters import rangesifter

class BSSiftRangesProxyModel(QtCore.QSortFilterProxyModel):
	"""Present sift-able ranges, based on bin column visibility"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._sort_collator = QtCore.QCollator()
		self._sort_collator.setNumericMode(True)
		self._sort_collator.setLocale(QtCore.QLocale.system())
		self._sort_collator.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

		self.setSortRole(QtCore.Qt.ItemDataRole.DisplayRole)
		self.setDynamicSortFilter(True)
		self.sort(0, QtCore.Qt.SortOrder.AscendingOrder)

	def rangeInfoForColumnDependency(self, field_id:avbutils.bins.BinColumnFieldIDs) -> rangesifter.BSSiftRangeInfo|None:

		return rangesifter.SIFT_RANGE_COLUMN_DEPENDENCIES.get(field_id)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if source_parent.isValid():
			return False

		field_id:avbutils.bins.BinColumnFormat = self.sourceModel()\
			.index(source_row, 0, QtCore.QModelIndex())\
			.data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		
		return bool(self.rangeInfoForColumnDependency(field_id))
	
	def lessThan(self, source_left:QtCore.QModelIndex, source_right:QtCore.QModelIndex):
		
		return self._sort_collator.compare(
			source_left .data(self.sortRole()),
			source_right.data(self.sortRole()),
		)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		
		field_id:avbutils.bins.BinColumnFormat = self.mapToSource(index).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		range_trigger = self.rangeInfoForColumnDependency(field_id)

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return range_trigger.range_name
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return range_trigger.range_role
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:

			format_name = avbutils.bins.BinColumnFormat(
				self.mapToSource(index).data(
					binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole
				)).name
			
			return self.tr("Sift based on {format_type} range").format(format_type=format_name)
		
		return super().data(index, role)