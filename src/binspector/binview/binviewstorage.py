"""
Watch a folder for changes
"""
import typing
from os import PathLike
from PySide6 import QtCore

from . import binviewsprovider

class BSBinViewStorageManager(QtCore.QObject):

	sig_binviews_added     = QtCore.Signal(object)
	sig_binviews_removed   = QtCore.Signal(object)
	sig_binviews_refreshed = QtCore.Signal(object)

	def __init__(self, *args, folder_path:PathLike[str], **kwargs):

		super().__init__(*args, **kwargs)

		self._folder_path = folder_path
		self._last_files  = self._getLatestFiles()

	def _getLatestFiles(self) -> list[QtCore.QFileInfo]:

		return QtCore.QDir(self._folder_path).entryInfoList(
			"*.json",
			QtCore.QDir.Filter.NoDotAndDotDot|QtCore.QDir.Filter.Files|QtCore.QDir.Filter.Readable,
		)
	
	def lastBinViews(self) -> list[QtCore.QFileInfo]:

		return self._last_files
	
	@QtCore.Slot()
	def updateAvailableBinViews(self):

		latest_files = self._getLatestFiles()

		files_new = set(latest_files) - set(self._last_files)
		files_del = set(self._last_files) - set(latest_files)

		self._last_files = latest_files

		if files_new:
			self.sig_binviews_added.emit(list(files_new))
		
		if files_del:
			self.sig_binviews_removed.emit(list(files_del))

		self.sig_binviews_refreshed.emit(latest_files)