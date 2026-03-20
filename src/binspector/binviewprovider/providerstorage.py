"""
Watch a folder for changes
"""

from __future__ import annotations

import logging, typing
from os import PathLike
from PySide6 import QtCore

from . import binviewsources
from ..binview import binviewitemtypes, jsonadapter



DEFAULT_SUBFOLDER_NAME    = "binviews"
DEFAULT_REFRESH_RATE_MSEC = 10_000

class BSBinViewStorageManager(QtCore.QObject):
	"""Read, write, and watch them bin views on them disks"""

	sig_binviews_added     = QtCore.Signal(object)
	sig_binviews_removed   = QtCore.Signal(object)
	sig_binviews_refreshed = QtCore.Signal(object)
	sig_storage_error      = QtCore.Signal()

	def __init__(self, *args, base_path:PathLike[str], not_exist_ok:bool=True, auto_refresh_interval:int=0, **kwargs):

		super().__init__(*args, **kwargs)

		self._base_dir      = QtCore.QDir(base_path)
		self._subfolder     = DEFAULT_SUBFOLDER_NAME
		self._last_files_info    = self.__getLatestFiles()

		self._refresh_timer = QtCore.QTimer()
		self._refresh_timer.timeout.connect(self.refreshBinViews)
		self.setRefreshInterval(auto_refresh_interval)

		self._currently_checking = False

		# Setup binview folder if it's not there
		# TODO: Maybe also install defaults if not there

		if not QtCore.QFileInfo(self.binViewStorageFolderPath()).isDir():
			
			if not not_exist_ok:
				raise FileNotFoundError(f"Not a valid directory: {base_path}")
			
			self._base_dir.mkdir(self._subfolder)

	@QtCore.Slot(int)
	def setRefreshInterval(self, refresh_msec:int):

		self._refresh_timer.stop()
		self._refresh_timer.setInterval(refresh_msec)

		logging.getLogger(__name__).debug("Set refresh interval to %s msec", refresh_msec)
		
		if refresh_msec:
			self._refresh_timer.start()

	@QtCore.Slot(str)
	def binViewStorageFolderPath(self) -> str:

		return QtCore.QDir.toNativeSeparators(self._base_dir.absoluteFilePath(self._subfolder))

	def __getLatestFiles(self) -> list[QtCore.QFileInfo]:
		"""For internal use only, use `refreshBinViews()` for bidniss"""

		if not QtCore.QFileInfo(self.binViewStorageFolderPath()).isDir():
			
			logging.getLogger(__name__).debug("Binview path not found during check: %s", self.binViewStorageFolderPath())

			self.sig_storage_error.emit()
			return []

		return QtCore.QDir(self.binViewStorageFolderPath()).entryInfoList(
			"*.json",
			QtCore.QDir.Filter.NoDotAndDotDot|QtCore.QDir.Filter.Files|QtCore.QDir.Filter.Readable,
		)
	
	def lastBinViews(self) -> list[binviewsources.BSBinViewSourceFile]:
		"""Last-seen bin views (not a live refresh)"""

		return [self._binSourceInfo(f) for f in self._last_files_info]
	
	@QtCore.Slot()
	def refreshBinViews(self):
		"""Refresh the bin views and emit signals"""

		# TODO: Do this whole thing in another thread

		if self._currently_checking:
			logging.getLogger(__name__).debug("Skipped bin view storage refresh, looks like we're still checking. CONCERNING? YES.")
			return
		
		self._currently_checking = True

		logging.getLogger(__name__).debug("Checking binview path %s...", self.binViewStorageFolderPath())

		latest_files = self.__getLatestFiles()

		files_new = set(f.absoluteFilePath() for f in latest_files) - set(f.absoluteFilePath() for f in self._last_files_info)
		files_del = set(f.absoluteFilePath() for f in self._last_files_info) - set(f.absoluteFilePath() for f in latest_files)

		logging.getLogger(__name__).debug("Found %s new binviews; %s disappeared", len(files_new), len(files_del))

		self._last_files_info = latest_files

		if files_new:
			print("Got new", files_new)
			self.sig_binviews_added.emit([self._binSourceInfo(QtCore.QFileInfo(f)) for f in files_new])
		
		if files_del:
			print("Got del", files_del)
			self.sig_binviews_removed.emit([self._binSourceInfo(QtCore.QFileInfo(f), not_exist_ok=True) for f in files_del])

		if files_new or files_del:
			self.sig_binviews_refreshed.emit([self._binSourceInfo(f) for f in latest_files])

		self._currently_checking = False

		if self._refresh_timer.interval():
			self._refresh_timer.start()

	def deleteStoredBinView(self, binview_source:binviewsources.BSBinViewSourceFile):
		"""Delete a stored bin view file from storage"""

		binview_path = binview_source.path()
		
		if not QtCore.QFileInfo(binview_path).isFile():
			raise FileNotFoundError(f"Requested bin view {binview_source.name()} was not found at expected path {binview_source.path()}")

		binview_file = QtCore.QFile(binview_path)

		if not binview_file.remove():

			if binview_file.error() != QtCore.QFileDevice.FileError.NoError:
				raise OSError(f"Could not delete binview source at {binview_path}: {binview_file.errorString()}")
			else:
				raise OSError(f"Could not delete binview source at {binview_path}: Unknown Error")
		
		self.refreshBinViews()

	def writeStoredBinView(self, binview_info:binviewitemtypes.BSBinViewInfo, format_adapter:jsonadapter.BSBinViewAbstractAdapter|None=None) -> str:
		"""Write a given bin view to storage"""

		format_adapter   = format_adapter or jsonadapter.BSBinViewJsonAdapter()
		path_binview_dir = self.binViewStorageFolderPath()

		if not QtCore.QDir().mkpath(path_binview_dir):
			raise OSError(f"Could not create binview folder path at {path_binview_dir}")
		
		path_binview_file = QtCore.QDir.toNativeSeparators(QtCore.QDir(path_binview_dir).filePath(binview_info.name + ".json"))

		tempfile = QtCore.QTemporaryFile(QtCore.QDir(path_binview_dir).filePath(".XXXXXX.tmp"))

		if not tempfile.open():
			raise OSError(f"Cannot create binview tempfile: {tempfile.errorString()}")

		if not tempfile.write(
			format_adapter.from_binview(binview_info).encode("utf-8")
		):
			raise OSError(f"Cannot write to binview tempfile: {tempfile.errorString()}")
		
		handle_binview_file = QtCore.QFile(path_binview_file)
		if handle_binview_file.exists() and not handle_binview_file.remove():
			raise OSError(f"Cannot replace existing binview at {path_binview_file}: {handle_binview_file.errorString()}")

		tempfile.flush()
		tempfile.setAutoRemove(False) # Don't autoremove after rename

		if not tempfile.rename(path_binview_file):
			raise OSError(f"Cannot update stored binview: {tempfile.error()}")

		self.refreshBinViews()

		return path_binview_file


	def _binSourceInfo(self, fileinfo:QtCore.QFileInfo, not_exist_ok:bool=False) -> binviewsources.BSBinViewSourceFile:

		return binviewsources.BSBinViewSourceFile(
			fileinfo.absoluteFilePath(),
			fileinfo.completeBaseName(),
			not_exist_ok
		)