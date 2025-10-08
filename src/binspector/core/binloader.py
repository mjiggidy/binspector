from os import PathLike
from PySide6 import QtCore
from ..models import viewmodelitems

import avb, avbutils, timecode

class BinViewLoader(QtCore.QRunnable):
	"""Load a given bin"""

	class Signals(QtCore.QObject):

		sig_begin_loading = QtCore.Signal()
		sig_got_display_mode = QtCore.Signal(object)
		sig_got_bin_appearance_settings = QtCore.Signal(object, object, object, object, object, object, object)
		sig_got_display_options = QtCore.Signal(object)
		sig_got_view_settings = QtCore.Signal(object)
		sig_got_mob = QtCore.Signal(object)
		sig_got_sort_settings = QtCore.Signal(object)
		sig_got_sift_settings = QtCore.Signal(bool, object)
		sig_done_loading = QtCore.Signal()

	def __init__(self, bin_path:PathLike, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._bin_path = bin_path
		self._signals  = self.Signals()
	
	def run(self):
		self._signals.sig_begin_loading.emit()

		with avb.open(self._bin_path) as bin_handle:
			
			self._loadBinDisplayItemTypes(bin_handle.content)
			self._loadBinView(bin_handle.content)
			self._loadBinDisplayMode(bin_handle.content)
			self._loadBinSiftSettings(bin_handle.content.sifted, bin_handle.content.sifted_settings)
			self._loadBinSorting(bin_handle.content.sort_columns)
			self._loadBinAppearanceSettings(bin_handle.content)
			
			for bin_item in bin_handle.content.items:
				try:
					self._loadCompositionMob(bin_item)
				except Exception as e:
					print(f"{e} {bin_item.mob}")
		
		self._signals.sig_done_loading.emit()

	def _loadBinDisplayMode(self, bin_content:avb.bin.Bin):
		"""Load the display mode"""

		self.signals().sig_got_display_mode.emit(avbutils.BinDisplayModes.get_mode_from_bin(bin_content))

	def _loadBinAppearanceSettings(self, bin_content:avb.bin.Bin):
		"""General and misc appearance settings stored around the bin"""

		# Sus out that font name
		# Try for Bin Font Name (strongly preferred), or fall back on mac font index (not likely to work)
		if "attributes" in bin_content.property_data and "ATTR__BIN_FONT_NAME" in bin_content.attributes:
			bin_font = bin_content.attributes["ATTR__BIN_FONT_NAME"]
		else:
			bin_font = bin_content.mac_font

		# Try to load bin column widths from the "BIN_COLUMNS_WIDTHS" bytearray, which decodes to a JSON string
		# I'm decoding it as UTF-8 but I almost doubt that's truly what it is.
		try:
			import json
			bin_column_widths = json.loads(bin_content.attributes.get("BIN_COLUMNS_WIDTHS",{}).decode("utf-8"))
		except:
			bin_column_widths = {}

		self.signals().sig_got_bin_appearance_settings.emit(
			bin_font,
			bin_content.mac_font_size,
			bin_content.forground_color,
			bin_content.background_color,
			bin_column_widths,
			bin_content.home_rect,
			bin_content.was_iconic,
		)
		
	def _loadBinDisplayItemTypes(self, bin_content:avb.bin.Bin):
		self._signals.sig_got_display_options.emit(avbutils.BinDisplayItemTypes.get_options_from_bin(bin_content))
	
	def _loadBinView(self, bin_content:avb.bin.Bin):
		
		bin_view = bin_content.view_setting
		bin_view.property_data = avb.core.AVBPropertyData(bin_view.property_data) # Dereference before closing file
		
		self._signals.sig_got_view_settings.emit(bin_view)
	
	def _loadBinSiftSettings(self, is_sifted:bool, sifted_settings:list[avb.bin.SiftItem]):
		self._signals.sig_got_sift_settings.emit(is_sifted, sifted_settings)
	
	def _loadBinSorting(self, bin_sorting:list):
		self.signals().sig_got_sort_settings.emit(bin_sorting)

	def _loadCompositionMob(self, bin_item:avb.bin.BinItem):
			
			#if not bin_item.user_placed:
			#	return
			
			bin_item_role = avbutils.BinDisplayItemTypes.from_bin_item(bin_item)
			#print(display_options)

			comp = bin_item.mob


			tape_name = None
			source_file_name = None
			timecode_range = None
			user_attributes = dict()
			source_drive = None

			if avbutils.BinDisplayItemTypes.SEQUENCE in bin_item_role:
				timecode_range = avbutils.get_timecode_range_for_composition(comp)
				user_attributes = comp.attributes.get("_USER",{})

			else:

				#primary_track = avbutils.format_track_label(avbutils.sourcerefs.primary_track_for_composition(comp))

				if avbutils.sourcerefs.composition_has_physical_source(comp):
				
					if avbutils.sourcerefs.physical_source_type_for_composition(comp) == avbutils.SourceMobRole.SOURCE_FILE:
						source_file_name = avbutils.sourcerefs.physical_source_name_for_composition(comp)
					else:
						tape_name = avbutils.sourcerefs.physical_source_name_for_composition(comp)
				
				# Drive info
				if "descriptor" in comp.property_data and isinstance(comp.descriptor, avb.essence.MediaDescriptor) and isinstance(comp.descriptor.locator, avb.misc.MSMLocator):
					source_drive = comp.descriptor.locator.last_known_volume
				else:
					try:
					# TODO: Do if comp itself is file source first, otherwise...
						file_source_clip, offset = next(avbutils.file_references_for_component(avbutils.primary_track_for_composition(comp).component))
					except StopIteration as e:
						#print("No file soruce:",comp)
						pass
					else:
						if isinstance(file_source_clip.mob.descriptor.locator, avb.misc.MSMLocator):
							source_drive = file_source_clip.mob.descriptor.locator.last_known_volume
							#print(source_drive)
				
				# Timecode
				# NOTE: This is all pretty sloppy here.
				try:
					timecode_range = avbutils.get_timecode_range_for_composition(comp)
				except Exception as e:
					pass

				attributes_reverse = []
				for source, offset in avbutils.source_references_for_component(avbutils.sourcerefs.primary_track_for_composition(comp).component):
					
					if "attributes" in source.mob.property_data:
						attributes_reverse.append(source.mob.attributes.get("_USER",{}))
					
					# Timecode
					try:
						tc_track = next(avbutils.get_tracks_from_composition(source.mob, type=avbutils.TrackTypes.TIMECODE, index=1))
					except:
						pass
					else:
						tc_component, offset = avbutils.resolve_base_component_from_component(tc_track.component, offset + source.start_time)
						
						if not isinstance(tc_component, avb.components.Timecode):
							print("Hmm",tc_component)
							continue
						
						timecode_range = timecode.TimecodeRange(
							start = timecode.Timecode(tc_component.start + offset.frame_number, rate=offset.rate),
							duration=comp.length
						)
				for a in reversed(attributes_reverse):
					user_attributes.update(a)
				if "attributes" in comp.property_data:
					user_attributes.update(comp.attributes.get("_USER",{}))

			markers = avbutils.get_markers_from_timeline(comp)

			item = {
				avbutils.BIN_COLUMN_ROLES["Name"]: comp.name or "",
				avbutils.BIN_COLUMN_ROLES["Color"]: viewmodelitems.TRTClipColorViewItem(avbutils.composition_clip_color(comp) if avbutils.composition_clip_color(comp) else None),
				avbutils.BIN_COLUMN_ROLES["Start"]: timecode_range.start if timecode_range else "",
				avbutils.BIN_COLUMN_ROLES["End"]: timecode_range.end if timecode_range else "",
				avbutils.BIN_COLUMN_ROLES["Duration"]: viewmodelitems.TRTDurationViewItem(timecode_range.duration) if timecode_range else "",
				avbutils.BIN_COLUMN_ROLES["Modified Date"]: comp.last_modified,
				avbutils.BIN_COLUMN_ROLES["Creation Date"]: comp.creation_time,
				avbutils.BIN_COLUMN_ROLES[""]: bin_item_role,
				avbutils.BIN_COLUMN_ROLES["Marker"]: viewmodelitems.TRTMarkerViewItem(markers[0]) if markers else None,
				avbutils.BIN_COLUMN_ROLES["Tracks"]: avbutils.format_track_labels(list(avbutils.get_tracks_from_composition(comp))) or None,
				avbutils.BIN_COLUMN_ROLES["Tape"]: tape_name or "",
				avbutils.BIN_COLUMN_ROLES["Drive"]: source_drive or "",
				avbutils.BIN_COLUMN_ROLES["Source File"]: source_file_name or "",
				avbutils.BIN_COLUMN_ROLES["Scene"]: user_attributes.get("Scene") or "",
				avbutils.BIN_COLUMN_ROLES["Take"]: user_attributes.get("Take") or "",
			}

			for key, val in user_attributes.items():
				item.update({"40_"+key: val})
			
			self._signals.sig_got_mob.emit(item)
	
	def signals(self) -> Signals:
		return self._signals