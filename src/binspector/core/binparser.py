"""
Functions for creating and returning data model items from a bin
Also used by `.binloader`
"""

import avb, avbutils, timecode
from ..models import viewmodelitems

def bin_display_flags_from_bin(bin_content:avb.bin.Bin) -> avbutils.BinDisplayItemTypes:
	return avbutils.BinDisplayItemTypes.get_options_from_bin(bin_content)
	
def bin_view_setting_from_bin(bin_content:avb.bin.Bin) -> avb.bin.BinViewSetting:
	
	bin_view = bin_content.view_setting
	bin_view.property_data = avb.core.AVBPropertyData(bin_view.property_data) # Dereference before closing file
	
	return bin_view

def bin_frame_view_scale_from_bin(bin_content:avb.bin.Bin) -> int:
	"""Get the Frame view mode scale"""

	return bin_content.mac_image_scale

def bin_column_widths_from_bin(bin_content:avb.bin.Bin) -> dict[str, int]:
	"""Decode bin column widths"""

	try:
		import json
		bin_column_widths = json.loads(bin_content.attributes.get("BIN_COLUMNS_WIDTHS",{}).decode("utf-8"))
	except Exception as e:
		#print(e)
		bin_column_widths = {}
	
	return bin_column_widths
	
def sift_settings_from_bin(bin_content:avb.bin.Bin) -> tuple[bool, list[avbutils.bins.BinSiftOption]]:
	return avbutils.bins.BinSiftOption.from_bin(bin_content)
	
def sort_settings_from_bin(bin_content:avb.bin.Bin) -> list[list[int, str]]:
	return bin_content.sort_columns

def display_mode_from_bin(bin_content:avb.bin.Bin) -> avbutils.BinDisplayModes:
	"""Load the display mode"""

	return avbutils.BinDisplayModes.get_mode_from_bin(bin_content)

def appearance_settings_from_bin(bin_content:avb.bin.Bin) -> tuple:
	"""General and misc appearance settings stored around the bin"""

	# Sus out that font name
	# Try for Bin Font Name (strongly preferred), or fall back on mac font index (not likely to work)
	if "attributes" in bin_content.property_data and "ATTR__BIN_FONT_NAME" in bin_content.attributes:
		bin_font = bin_content.attributes["ATTR__BIN_FONT_NAME"]
	else:
		bin_font = bin_content.mac_font

	# SKIP: This is now handled via binview.  Need to update the signal here
	bin_column_widths = {}

	return (
		bin_font,
		bin_content.mac_font_size,
		bin_content.forground_color,
		bin_content.background_color,
		bin_column_widths,
		bin_content.home_rect,
		bin_content.was_iconic,
	)

import dataclasses
@dataclasses.dataclass(frozen=True)
class BinItemInfo:
	"""Bin item info for a given mob"""

	mob_id            :avb.mobid.MobID
	item_type         :avbutils.bins.BinDisplayItemTypes
	tracks            :set[avb.trackgroups.Track]
	clip_color        :avbutils.compositions.ClipColor|None
	name              :str
	frame_coordinates :tuple[int,int]|None
	keyframe_offset   :int
	view_items        :dict[int,viewmodelitems.LBAbstractViewItem|dict[str,str]]	# Field ID -> ViewItem or 40 -> dict[term,def]


def load_item_from_bin(bin_item:avb.bin.BinItem) -> dict:
		"""Parse a mob and its bin item properties"""

		
		comp:avb.trackgroups.Composition = bin_item.mob

		# Get frame scale to normalize frame coords below

		# NOTE BOUD DIS:
		
		# The bin seems to store x,y coords of the THUMBNAIL specifically
		# (not the whole "item" with padding, margins, outline, label, etc)
		# These coordinates are stored PREMULTIPLEID by the zoom factor

		# I'm preferring to normalize these coordinates to zoom=1.0 and top-left
		# coordinates refer to the top-left of the item proper

		# This is still very TODO

		frame_scale_x = bin_frame_view_scale_from_bin(bin_item.root.content)
		frame_scale_y = 74 + ((frame_scale_x - avbutils.bins.THUMB_FRAME_MODE_RANGE.start) * 10)
		mob_coords= ((bin_item.x-16) / frame_scale_x, (bin_item.y-16) / frame_scale_y * 14) 	# Y Unit * 14 height?
		
		# Initial data model info
		mob_id    = comp.mob_id
		mob_types = avbutils.BinDisplayItemTypes.from_bin_item(bin_item)
		mob_tracks= avbutils.timeline.get_tracks_from_composition(comp)
		mob_name  = comp.name
		mob_color = avbutils.compositions.composition_clip_color(comp)
		mob_frame = bin_item.keyframe

		# Prep defaults
		# TODO: Should be at least, like, some sort of struct
		tape_name = None
		source_file_name = None
		timecode_range = None
		user_attributes = dict()
		source_drive = None

		if avbutils.BinDisplayItemTypes.SEQUENCE in mob_types:
			timecode_range = avbutils.get_timecode_range_for_composition(comp)
			user_attributes = comp.attributes.get("_USER",{})

		else:

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
						import logging
						logging.getLogger(__name__).error("Got weird TC component for %s: %s", mob_name,tc_component)
						continue
					
					timecode_range = timecode.TimecodeRange(
						start = timecode.Timecode(tc_component.start + offset.frame_number, rate=offset.rate),
						duration=comp.length
					)
			for a in reversed(attributes_reverse):
				user_attributes.update(a)
			if "attributes" in comp.property_data:
				user_attributes.update(comp.attributes.get("_USER",{}))

		try:
			marker = next(avbutils.get_markers_from_timeline(comp))
		except StopIteration:
			marker = None

		item = {
			avbutils.BIN_COLUMN_ROLES["Name"]:  viewmodelitems.TRTStringViewItem(mob_name),
			avbutils.BIN_COLUMN_ROLES["Color"]: viewmodelitems.TRTClipColorViewItem(mob_color),
			avbutils.BIN_COLUMN_ROLES["Start"]: timecode_range.start if timecode_range else "",
			avbutils.BIN_COLUMN_ROLES["End"]: timecode_range.end if timecode_range else "",
			avbutils.BIN_COLUMN_ROLES["Duration"]: viewmodelitems.TRTDurationViewItem(timecode_range.duration) if timecode_range else "",
			avbutils.BIN_COLUMN_ROLES["Modified Date"]: comp.last_modified,
			avbutils.BIN_COLUMN_ROLES["Creation Date"]: comp.creation_time,
			avbutils.BIN_COLUMN_ROLES[""]: mob_types,
			avbutils.BIN_COLUMN_ROLES["Marker"]: viewmodelitems.TRTMarkerViewItem(marker) if marker else None,
			avbutils.BIN_COLUMN_ROLES["Tracks"]: viewmodelitems.TRTStringViewItem(avbutils.timeline.format_track_labels(mob_tracks)) or None,
			avbutils.BIN_COLUMN_ROLES["Tape"]: tape_name or "",
			avbutils.BIN_COLUMN_ROLES["Drive"]: source_drive or "",
			avbutils.BIN_COLUMN_ROLES["Source File"]: source_file_name or "",
			avbutils.BIN_COLUMN_ROLES["Scene"]: user_attributes.get("Scene") or "",
			avbutils.BIN_COLUMN_ROLES["Take"]: user_attributes.get("Take") or "",
			avbutils.BIN_COLUMN_ROLES["Labroll"]: user_attributes.get("Labroll") or "",
			avbutils.BIN_COLUMN_ROLES["Soundroll"]: user_attributes.get("Soundroll") or "",
			avbutils.BIN_COLUMN_ROLES["Camroll"]: user_attributes.get("Camroll") or "",
			avbutils.BIN_COLUMN_ROLES["FPS"]: user_attributes.get("FPS") or "",
			avbutils.BIN_COLUMN_ROLES["Sound TC"]: user_attributes.get("Sound TC") or "",
			avbutils.BIN_COLUMN_ROLES["Shoot Date"]: user_attributes.get("Shoot Date") or "",
			avbutils.BIN_COLUMN_ROLES["Audio SR"]: user_attributes.get("Audio SR") or "",
			
			
		}

		# Old
		#for key, val in user_attributes.items():
		#	item.update({"40_"+key: val})

		# New
		item.update({40: user_attributes})
		
		return BinItemInfo(
			name = mob_name,
			item_type = mob_types,
			view_items = item,
			frame_coordinates = mob_coords,
			keyframe_offset   = mob_frame,
			mob_id = mob_id,
			tracks=mob_tracks,
			clip_color=mob_color,
		)