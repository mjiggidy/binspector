import typing, dataclasses
from PySide6 import QtCore
import avbutils

from ..binview import binviewitemtypes
from ..binitems import binitemtypes

@dataclasses.dataclass(frozen=True)
class ColumnRangeTrigger:

	name:str
	range_role:binitemtypes.BSBinItemDataRoles

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

		self._range_triggers = {

			avbutils.bins.BinColumnFieldIDs.Start: ColumnRangeTrigger(
				name = self.tr("Start to End Range"),
				range_role= binitemtypes.BSBinItemDataRoles.TimecodeRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC1: ColumnRangeTrigger(
				name = self.tr("Auxiliary TC 1 Range"),
				range_role= binitemtypes.BSBinItemDataRoles.AuxTC1RangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC2: ColumnRangeTrigger(
				name = self.tr("Auxiliary TC 2 Range"),
				range_role= binitemtypes.BSBinItemDataRoles.AuxTC2RangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC3: ColumnRangeTrigger(
				name = self.tr("Auxiliary TC 3 Range"),
				range_role= binitemtypes.BSBinItemDataRoles.AuxTC3RangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC4: ColumnRangeTrigger(
				name = self.tr("Auxiliary TC 4 Range"),
				range_role= binitemtypes.BSBinItemDataRoles.AuxTC4RangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC5: ColumnRangeTrigger(
				name = self.tr("Auxiliary TC 5 Range"),
				range_role= binitemtypes.BSBinItemDataRoles.AuxTC5RangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.InkNumber: ColumnRangeTrigger(
				name = self.tr("Ink Number Range"),
				range_role= binitemtypes.BSBinItemDataRoles.InkNumberRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.MarkIn: ColumnRangeTrigger(
				name = self.tr("Mark In to Out Range"),
				range_role= binitemtypes.BSBinItemDataRoles.TCMarkInOutRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.AuxiliaryInk: ColumnRangeTrigger(
				name = self.tr("Auxiliary Ink Range"),
				range_role= binitemtypes.BSBinItemDataRoles.AuxInkNumberRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.KNMarkIn: ColumnRangeTrigger(
				name = self.tr("KN Mark In to Out Range"),
				range_role= binitemtypes.BSBinItemDataRoles.KNMarkInOutRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.FilmTC: ColumnRangeTrigger(
				name = self.tr("Film TC Range"),
				range_role= binitemtypes.BSBinItemDataRoles.FilmTCRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.KNStart: ColumnRangeTrigger(
				name = self.tr("KN Start to End Range"),
				range_role= binitemtypes.BSBinItemDataRoles.KNRangeRole,
			),

			avbutils.bins.BinColumnFieldIDs.SoundTC: ColumnRangeTrigger(
				name = self.tr("Sound TC Range"),
				range_role= binitemtypes.BSBinItemDataRoles.SoundTCRole,
			),

		}

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if source_parent.isValid():
			return False

		field_id:avbutils.bins.BinColumnFormat = self.sourceModel()\
			.index(source_row, 0, QtCore.QModelIndex())\
			.data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		
		return field_id in self._range_triggers
	
	def lessThan(self, source_left:QtCore.QModelIndex, source_right:QtCore.QModelIndex):
		
		return self._sort_collator.compare(
			source_left .data(self.sortRole()),
			source_right.data(self.sortRole()),
		)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		
		field_id:avbutils.bins.BinColumnFormat = self.mapToSource(index).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		range_trigger = self._range_triggers[field_id]

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return range_trigger.name
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return range_trigger.range_role
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:

			format_name = avbutils.bins.BinColumnFormat(
				self.mapToSource(index).data(
					binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole
				)).name
			
			return self.tr("Sift based on {format_type} range").format(format_type=format_name)
		
		return super().data(index, role)