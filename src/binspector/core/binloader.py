"""
`QRunnable` enabling threaded bin loading
Logic is implemented via `.binparser`
"""

from os import PathLike
from PySide6 import QtCore
import avb
from . import binparser

class BSBinViewLoader(QtCore.QRunnable):
	"""Load a given bin in a threadpool"""

	class Signals(QtCore.QObject):
		"""Signals emitted by `BSBinViewLoader`"""

		# Status signals
		sig_begin_loading = QtCore.Signal(str)
		sig_done_loading = QtCore.Signal()
		sig_aborted_loading = QtCore.Signal()
		sig_got_exception = QtCore.Signal(object)

		sig_got_mob_count = QtCore.Signal(int)

		sig_got_display_mode = QtCore.Signal(object)
		sig_got_bin_appearance_settings = QtCore.Signal(object, object, object, object, object, object, object)
		sig_got_bin_display_settings = QtCore.Signal(object)
		sig_got_view_settings = QtCore.Signal(object, object)
		sig_got_mob = QtCore.Signal(object)
		sig_got_sort_settings = QtCore.Signal(object)
		sig_got_sift_settings = QtCore.Signal(bool, object)

	def __init__(self, bin_path:PathLike, signals:Signals, *args, **kwargs):
		
		super().__init__(*args, **kwargs)
		
		self._bin_path = bin_path
		self._signals  = signals

	def signals(self) -> Signals:
		"""Return the signals instance"""

		return self._signals
	
	def run(self):
		"""Run the thing"""

		self._signals.sig_begin_loading.emit(self._bin_path)

		with avb.open(self._bin_path) as bin_handle:
			
			# Load bin properties
			try:
				self._signals.sig_got_bin_display_settings.emit(binparser.bin_display_flags_from_bin(bin_handle.content))
				self._signals.sig_got_view_settings.emit(binparser.bin_view_setting_from_bin(
					bin_handle.content), binparser.bin_column_widths_from_bin(bin_handle.content)
				)
				self._signals.sig_got_display_mode.emit(binparser.display_mode_from_bin(bin_handle.content))
				self._signals.sig_got_sift_settings.emit(*binparser.sift_settings_from_bin(bin_handle.content))
				self._signals.sig_got_sort_settings.emit(binparser.sort_settings_from_bin(bin_handle.content))
				self._signals.sig_got_bin_appearance_settings.emit(*binparser.appearance_settings_from_bin(bin_handle.content))

			except Exception as e:
				self._signals.sig_got_exception.emit(e)
				
			try:
				self._signals.sig_got_mob_count.emit(len(bin_handle.content.items))
			except Exception as e:
				print(e)

			# Load mobs
			for bin_item in bin_handle.content.items:

				try:
					self._signals.sig_got_mob.emit(binparser.load_item_from_bin(bin_item))
				except Exception as e:
					self._signals.sig_got_exception.emit(e)

		self._signals.sig_done_loading.emit()