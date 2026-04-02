from PySide6 import QtCore

class BSAbstractBinSortFilterProxyModel(QtCore.QSortFilterProxyModel):
	"""An abstract sort/filter proxy model"""

	sig_filter_toggled = QtCore.Signal(bool)

	def __init__(self, *args, is_enabled:bool=True, **kwargs):

		super().__init__(*args, **kwargs)

		self._is_enabled = is_enabled

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):
		"""To be implemented by subclasses.  Emit `sig_filter_toggled` at end"""
		pass

	def isEnabled(self) -> bool:
		
		return self._is_enabled