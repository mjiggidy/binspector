"""
Watch a folder for changes
"""

import logging
from os import PathLike
from PySide6 import QtCore

from ..binview import binviewsources

DEFAULT_SUBFOLDER_NAME    = "binviews"
DEFAULT_REFRESH_RATE_MSEC = 10_000

class BSBinViewStorageManager(QtCore.QObject):

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

		# Setup binview folder if it's not there
		# TODO: Maybe also install defaults if not there

		if not QtCore.QFileInfo(self.binViewStoragePath()).isDir():
			
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
	def binViewStoragePath(self) -> str:

		return QtCore.QDir.toNativeSeparators(self._base_dir.absoluteFilePath(self._subfolder))

	def __getLatestFiles(self) -> list[QtCore.QFileInfo]:
		"""For internal use only"""

		if not QtCore.QFileInfo(self.binViewStoragePath()).isDir():
			
			logging.getLogger(__name__).debug("Binview path not found during check: %s", self.binViewStoragePath())

			self.sig_storage_error.emit()
			return []

		return QtCore.QDir(self.binViewStoragePath()).entryInfoList(
			"*.json",
			QtCore.QDir.Filter.NoDotAndDotDot|QtCore.QDir.Filter.Files|QtCore.QDir.Filter.Readable,
		)
	
	def lastBinViews(self) -> list[binviewsources.BSBinViewSourceFile]:
		"""Last-seen bin views (not a live refresh)"""

		return [self._binSourceInfo(f) for f in self._last_files_info]
	
	@QtCore.Slot()
	def refreshBinViews(self):
		"""Refresh the bin views and emit signals"""

		logging.getLogger(__name__).debug("Checking binview path %s...", self.binViewStoragePath())

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

		if self._refresh_timer.interval():
			self._refresh_timer.start()

	def _binSourceInfo(self, fileinfo:QtCore.QFileInfo, not_exist_ok:bool=False) -> binviewsources.BSBinViewSourceFile:

		return binviewsources.BSBinViewSourceFile(
			fileinfo.absoluteFilePath(),
			fileinfo.completeBaseName(),
			not_exist_ok
		)