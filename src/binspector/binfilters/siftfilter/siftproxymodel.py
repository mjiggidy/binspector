import typing
from PySide6 import QtCore

from .. import abstractfiltermodel

from .siftoptions.abstractoption import BSBinSiftAbstractOption

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	def __init__(self, *args, sift_options:list[BSBinSiftAbstractOption]|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._sift_options = sift_options or []

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):

		if self._is_enabled == is_enabled:
			return

		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)
	
	@QtCore.Slot(object)
	def setSiftOptions(self, sift_options:typing.Iterable[BSBinSiftAbstractOption]):

		if self._sift_options == sift_options:
			return

		self.beginFilterChange()

		self._sift_options = list(sift_options)
		
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self.isEnabled():
			return True
		
		if source_parent.isValid():
			return False
		
		source_index = self.sourceModel().index(source_row, 0, QtCore.QModelIndex())

		return all(option.option_accepts_row(source_index) for option in self._sift_options)