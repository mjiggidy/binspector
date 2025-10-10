from os import PathLike
from PySide6 import QtCore
import avb
from . import binparser

class BSBinViewLoader(QtCore.QRunnable):
	"""Load a given bin"""

	class Signals(QtCore.QObject):

		sig_begin_loading = QtCore.Signal()
		sig_got_display_mode = QtCore.Signal(object)
		sig_got_bin_appearance_settings = QtCore.Signal(object, object, object, object, object, object, object)
		sig_got_bin_display_settings = QtCore.Signal(object)
		sig_got_view_settings = QtCore.Signal(object)
		sig_got_mob = QtCore.Signal(object)
		sig_got_sort_settings = QtCore.Signal(object)
		sig_got_sift_settings = QtCore.Signal(bool, object)
		sig_done_loading = QtCore.Signal()

	def __init__(self, bin_path:PathLike, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._bin_path = bin_path
		self._signals  = self.Signals()

	def signals(self) -> Signals:
		return self._signals
	
	def run(self):
		self._signals.sig_begin_loading.emit()

		with avb.open(self._bin_path) as bin_handle:
			
			self._signals.sig_got_bin_display_settings.emit(binparser.bin_display_flags_from_bin(bin_handle.content))
			self._signals.sig_got_view_settings.emit(binparser.bin_view_setting_from_bin(bin_handle.content))
			self._signals.sig_got_display_mode.emit(binparser.display_mode_from_bin(bin_handle.content))
			self._signals.sig_got_sift_settings.emit(*binparser.sift_settings_from_bin(bin_handle.content))
			self._signals.sig_got_sort_settings.emit(binparser.sort_settings_from_bin(bin_handle.content))
			self._signals.sig_got_bin_appearance_settings.emit(*binparser.appearance_settings_from_bin(bin_handle.content))
			
			for bin_item in bin_handle.content.items:
				try:
					self._signals.sig_got_mob.emit(binparser._loadCompositionMob(bin_item))
				except Exception as e:
					print(f"{e} {bin_item.mob}")
		
		self._signals.sig_done_loading.emit()


	
