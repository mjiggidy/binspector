from PySide6 import QtCore

"""
Manage QSettings location & format
"""

import logging
from os import PathLike
from PySide6 import QtCore

LATEST_CONFIG_VERSION = 1
"""Latest config version"""

class BSSettingsManager:

	def __init__(self, format:QtCore.QSettings.Format=QtCore.QSettings.Format.IniFormat, basepath:PathLike|None=None):

		self._format   = format
		self._basepath = QtCore.QDir(basepath)

		self._checkVersion()
	
	def basePath(self) -> PathLike:
		"""The current path"""
		return self._basepath
	
	def format(self) -> QtCore.QSettings.Format:
		"""The file format used for settings"""
		return self._format
	
	def settings(self, feature_name:str) -> QtCore.QSettings:
		"""Get a settings handler for a given feature"""

		if self.format() == QtCore.QSettings.Format.IniFormat:
			settings = QtCore.QSettings(self.settingsPath(feature_name), QtCore.QSettings.Format.IniFormat)
			logging.debug("Initialized settings for %s at %s", feature_name, self.settingsPath(feature_name))
			return settings
		else:
			return QtCore.QSettings(self.format())
	
	def settingsPath(self, feature_name:str) -> PathLike[str]:
		return self._basepath.filePath(feature_name + "_config.ini")
	
	def _checkVersion(self):
		"""Check settings version and migrate if needed"""

		user_settings_ver = self.settings("app").value("Config/config_version", None, int)

		if not user_settings_ver:
			self.settings("app").setValue("Config/config_version", LATEST_CONFIG_VERSION)
		elif user_settings_ver != LATEST_CONFIG_VERSION:
			# TODO
			logging.debug("Migrate user config from %i to %i", user_settings_ver, LATEST_CONFIG_VERSION)