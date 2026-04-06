import typing
from PySide6 import QtCore
import avbutils
from . import abstractfiltermodel

class BSBinSiftFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):

		if self._is_enabled == is_enabled:
			return

		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)
	
	@QtCore.Slot(object)
	def setSiftOptions(self, sift_options:typing.Iterable[avbutils.bins.BinSiftOption]):

		print("TODO")