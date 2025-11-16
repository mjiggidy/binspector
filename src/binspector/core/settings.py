from PySide6 import QtCore

"""
Manage QSettings location & format
"""

import logging, enum
from os import PathLike
from PySide6 import QtCore

class BSStartupBehavior(enum.StrEnum):

	EMPTY_WINDOW = "Show Empty Window"
	SHOW_BROWSER = "Show File Browser"
	LAST_BIN     = "Open Last Bin"

LATEST_CONFIG_VERSION = 1
"""Latest config version"""

class BSSettingsManager:

	def __init__(self, format:QtCore.QSettings.Format=QtCore.QSettings.Format.IniFormat, basepath:PathLike|None=None):

		self._format   = format
		self._basepath = QtCore.QDir(basepath)

		logging.getLogger(__name__).debug("Initialized settings manager at %s", self._basepath.absolutePath())

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
			#logging.getLogger(__name__).debug("Initialized settings for %s at %s", feature_name, self.settingsPath(feature_name))
			return settings
		else:
			return QtCore.QSettings(self.format())
	
	def settingsPath(self, feature_name:str) -> PathLike[str]:
		return self._basepath.filePath(feature_name + "_config.ini")
	
	def _checkVersion(self):
		"""Check settings version and migrate if needed"""

		user_settings_ver = self.settings("bs").value("Config/config_version", None, int)

		if not user_settings_ver:
			self.settings("bs").setValue("Config/config_version", LATEST_CONFIG_VERSION)
		elif user_settings_ver != LATEST_CONFIG_VERSION:
			# TODO
			logging.getLogger(__name__).debug("Migrate user config from %i to %i", user_settings_ver, LATEST_CONFIG_VERSION)
	
	def currentSettingsVersion(self) -> int|None:

		current_settings_version = self.settings("bs").value("Config/config_version", None, int)
		logging.getLogger(__name__).debug("Returning config_version: %s", current_settings_version)
		return current_settings_version

	@QtCore.Slot(object)
	def setLastBinPath(self, bin_path:PathLike):

		self.settings("bs").setValue("Session/last_bin", str(bin_path))
		logging.getLogger(__name__).debug("Set last_bin: %s", bin_path)

	def lastBinPath(self) -> PathLike[str]:

		bin_path = self.settings("bs").value("Session/last_bin", None, str)
		logging.getLogger(__name__).debug("Returning last_bin: %s", bin_path)
		return bin_path
	
	@QtCore.Slot(QtCore.QRect)
	def setLastWindowGeometry(self, rect:QtCore.QRect):

		self.settings("bs").setValue("Session/last_window_geometry", QtCore.QRect(rect))
		logging.getLogger(__name__).debug("Set last_window_geometry: %s", rect)
	
	def lastWindowGeometry(self) -> QtCore.QRect:

		last_rect = self.settings("bs").value("Session/last_window_geometry", None, QtCore.QRect)
		logging.getLogger(__name__).debug("Returning last_window_geomoetry: %s", last_rect)
		return last_rect
	
	@QtCore.Slot(bool)
	def setSoftwareUpdateAutocheckEnabled(self, is_enabled:bool):

		self.settings("bs").setValue("SoftwareUpdates/auto_check_for_updates", bool(is_enabled))
		logging.getLogger(__name__).debug("Set auto_check_for_updates: %s", is_enabled)
	
	def softwareUpdateAutocheckEnabled(self) -> bool:

		is_enabled = self.settings("bs").value("SoftwareUpdates/auto_check_for_updates", True, bool)
		logging.getLogger(__name__).debug("Returning auto_check_for_updates: %s", is_enabled)
		return is_enabled
	
	@QtCore.Slot(bool)
	def setBinViewEnabled(self, is_enabled:bool):

		self.settings("bs").setValue("BinSettingsToggles/use_bin_view", is_enabled)
		logging.getLogger(__name__).debug("Set use_bin_view: %s", is_enabled)
	
	def binViewIsEnabled(self) -> bool:
		
		is_enabled = self.settings("bs").value("BinSettingsToggles/use_bin_view", True, bool)
		logging.getLogger(__name__).debug("Returning use_bin_view: %s", is_enabled)
		return is_enabled
	
	@QtCore.Slot(bool)
	def setBinFiltersEnabled(self, is_enabled:bool):

		self.settings("bs").setValue("BinSettingsToggles/use_bin_filters", is_enabled)
		logging.getLogger(__name__).debug("Set use_bin_filters: %s", is_enabled)
	
	def binFiltersEnabled(self) -> bool:
		
		is_enabled = self.settings("bs").value("BinSettingsToggles/use_bin_filters", True, bool)
		logging.getLogger(__name__).debug("Returning use_bin_filters: %s", is_enabled)
		return is_enabled
	
	@QtCore.Slot(bool)
	def setBinAppearanceEnabled(self, is_enabled:bool):

		self.settings("bs").setValue("BinSettingsToggles/use_bin_appearance", is_enabled)
		logging.getLogger(__name__).debug("Set use_bin_appearance: %s", is_enabled)
	
	def binAppearanceIsEnabled(self) -> bool:
		
		is_enabled = self.settings("bs").value("BinSettingsToggles/use_bin_appearance", True, bool)
		logging.getLogger(__name__).debug("Returning use_bin_appearance: %s", is_enabled)
		return is_enabled
	
	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):

		self.settings("bs").setValue("BinLoading/mob_queue_size", queue_size)
		logging.getLogger(__name__).debug("Set mob_queue_size: %s", queue_size)

	def mobQueueSize(self) -> int:
		
		queue_size = self.settings("bs").value("BinLoading/mob_queue_size", 500, int)
		logging.getLogger(__name__).debug("Returning mob_queue_size: %s", queue_size)
		return queue_size
	
	@QtCore.Slot(int)
	def setUseFancyProgressBar(self, use_animation:bool):

		self.settings("bs").setValue("BinLoading/fancy_progress_bar", use_animation)
		logging.getLogger(__name__).debug("Set fancy_progress_bar: %s", use_animation)

	def useFancyProgressBar(self) -> int:
		
		use_animation = self.settings("bs").value("BinLoading/fancy_progress_bar", True, bool)
		logging.getLogger(__name__).debug("Returning fancy_progress_bar: %s", use_animation)
		return use_animation
	
	@QtCore.Slot(object)
	def setStartupBehavior(self, behavior:BSStartupBehavior):

		self.settings("bs").setValue("Session/start_behavior", behavior)
		logging.getLogger(__name__).debug("Set start_behavior: %s", behavior)

	def startupBehavior(self) -> BSStartupBehavior:
		
		behavior_string = self.settings("bs").value("Session/start_behavior", BSStartupBehavior.SHOW_BROWSER.value, str)
		try:
			behavior = BSStartupBehavior(behavior_string)
		except ValueError:
			behavior = BSStartupBehavior.SHOW_BROWSER
			logging.getLogger(__name__).error("Invalid start_behavior=\"%s\"; default to: \"%s\"", behavior_string, behavior)
			
		logging.getLogger(__name__).debug("Returning start_behavior: %s", behavior)
		return behavior
	
	@QtCore.Slot(int)
	def setBottomScrollbarScale(self, scale_factor:int|float):

		self.settings("bs").setValue("Session/bottom_scrollbar_scale", scale_factor)
		logging.getLogger(__name__).debug("Set bottom_scrollbar_scale: %s", scale_factor)

	def bottomScrollbarScale(self) -> float:
		
		scale_factor = max(0.5, self.settings("bs").value("Session/bottom_scrollbar_scale", 1.25, float))
		logging.getLogger(__name__).debug("Returning bottom_scrollbar_scale: %s", scale_factor)
		return scale_factor

	def useFancyProgressBar(self) -> int:
		
		use_animation = self.settings("bs").value("BinLoading/fancy_progress_bar", True, bool)
		logging.getLogger(__name__).debug("Returning fancy_progress_bar: %s", use_animation)
		return use_animation