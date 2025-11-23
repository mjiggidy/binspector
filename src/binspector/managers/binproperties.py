import logging
import avb, avbutils
from PySide6 import QtCore, QtGui, QtWidgets
from ..models import viewmodelitems
from ..core import binparser
from . import base

TEMP_POSITION_OFFSET_THING = 10

class BSBinViewModeManager(QtCore.QObject):
	"""Manage them viewmodes"""

	sig_view_mode_changed = QtCore.Signal(object)
	"""The view mode has been changed"""

	def __init__(self, initial_mode:avbutils.BinDisplayModes=avbutils.BinDisplayModes.LIST, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._current_mode = initial_mode

	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current bin view mode"""

		if view_mode != self._current_mode:
			self._current_mode = view_mode
			self.sig_view_mode_changed.emit(self._current_mode)
	
	def viewMode(self) -> avbutils.BinDisplayModes:
		return self._current_mode

class BSBinViewManager(base.LBItemDefinitionView):

	sig_bin_view_changed = QtCore.Signal(object, object, int)
	"""Binview has been reset"""

	sig_view_mode_toggled = QtCore.Signal(object)
	"""Binview has been toggled on/off"""

	sig_all_columns_toggled = QtCore.Signal(object)
	"""All columns have been toggled on/off (opposite of `sig_view_mode_toggled`)"""

	sig_bin_filters_toggled = QtCore.Signal(object)
	"""Filters have been toggled on/off"""

	sig_all_items_toggled = QtCore.Signal(object)
	"""All items have been toggled on/off (opposite of `sig_bin_filters_toggled`)"""

	sig_focus_bin_column    = QtCore.Signal(str)
	"""Focus a given bin column index"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._default_sort_columns:list[list[int,str]] = []

		self._binview_is_enabled = True
		self._filters_enabled    = True

		# Emit the opposites
		self.sig_view_mode_toggled  .connect(lambda bv_enabled: self.sig_all_columns_toggled.emit(not bv_enabled))
		self.sig_bin_filters_toggled.connect(lambda fl_enabled: self.sig_all_items_toggled  .emit(not fl_enabled))

		#self.sig_all_columns_toggled.connect(lambda all_columns: print(f"{all_columns=}")) #Not?
		#self.sig_all_items_toggled.connect(lambda all_visible: print(f"{all_visible=}")) # Firing

	@QtCore.Slot(object, object, object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict|None=None, frame_view_scale:int=avbutils.THUMB_FRAME_MODE_RANGE.start):
		"""Set columns and their widths"""

		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order",  self.tr("Order")),
			viewmodelitems.LBAbstractViewHeaderItem("title",  self.tr("Title")),
			viewmodelitems.LBAbstractViewHeaderItem("format", self.tr("Format")),
			viewmodelitems.LBAbstractViewHeaderItem("type",   self.tr("Type")),
			viewmodelitems.LBAbstractViewHeaderItem("width",  self.tr("Width")),
			viewmodelitems.LBAbstractViewHeaderItem("hidden", self.tr("Is Hidden")),
		]
		
		for header in headers:
			super().addHeader(header)

		for idx, column in enumerate(bin_view.columns):
			column.update({
				"order": idx,
				"width": column_widths.get(column["title"],None)
			})
				
			self.addColumnDefinition(column)
		
		self.sig_bin_view_changed.emit(bin_view, column_widths, frame_view_scale)

	@QtCore.Slot(object)
	def setDefaultSortColumns(self, sort_settings:list[list[int,str]]):

		self._default_sort_columns = sort_settings

	def defaultSortColumns(self) -> list[list[int,str]]:

		return self._default_sort_columns

	@QtCore.Slot(object)
	def addColumnDefinition(self, column_definition:dict[str,object]):

		column_definition["format"] = avbutils.BinColumnFormat(column_definition["format"])
		self.addRow(column_definition)
	
	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		if is_enabled != self._binview_is_enabled:

			self._binview_is_enabled = is_enabled
			self.sig_view_mode_toggled.emit(self._binview_is_enabled)
	
	@QtCore.Slot(object)
	def setAllColumnsVisible(self, all_visibile:bool):
		"""Convenience method: Opposite of setBinViewEnabled"""

		self.setBinViewEnabled(not all_visibile)

	@QtCore.Slot(object)
	def setBinFiltersEnabled(self, is_enabled:bool):

		if is_enabled != self._filters_enabled:

			self._filters_enabled = is_enabled
			self.sig_bin_filters_toggled.emit(self._filters_enabled)
	
	@QtCore.Slot(object)
	def setAllItemsVisible(self, all_visible:bool):

		self.setBinFiltersEnabled(not all_visible)

	@QtCore.Slot(QtCore.QModelIndex)
	def requestFocusColumn(self, selected_index:QtCore.QModelIndex):

		
		# Field name
		#clicked_row  = selected_index.row()
		header_names = [selected_index.model().headerData(i, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole) for i in range(selected_index.model().columnCount())]
		
		selected_format  = selected_index.siblingAtColumn(header_names.index("Type")).data(QtCore.Qt.ItemDataRole.UserRole).raw_data()
		selected_name    = selected_index.siblingAtColumn(header_names.index("Title")).data(QtCore.Qt.ItemDataRole.DisplayRole)
		
		logging.getLogger(__name__).debug("Requesting to focus bin view column %s: %s", selected_format, selected_name)

		selected_field_name = f"{selected_format}_{selected_name}" if selected_format == 40 else str(selected_format)

		#print(selected_field_name)

		
		#print(selected_index.data(QtCore.Qt.ItemDataRole.UserRole))
		self.sig_focus_bin_column.emit(selected_field_name)


class BSBinDisplaySettingsManager(base.LBItemDefinitionView):

	sig_bin_display_changed = QtCore.Signal(object)

	def __init__(self):

		super().__init__()

	@QtCore.Slot(object)
	def setBinDisplayFlags(self, bin_display:avbutils.BinDisplayItemTypes):

		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("name",  self.tr("Name")),
			viewmodelitems.LBAbstractViewHeaderItem("value", self.tr("Value")),
		]
		
		for header in headers:
			self.addHeader(header)
		
		for f in bin_display:
			self.addRow({"name": f.name, "value": f.value})
		
		self.sig_bin_display_changed.emit(bin_display)
		
class BSBinAppearanceSettingsManager(base.LBItemDefinitionView):

	sig_font_changed           = QtCore.Signal(QtGui.QFont)
	sig_palette_changed        = QtCore.Signal(QtGui.QColor, QtGui.QColor)
	sig_column_widths_changed  = QtCore.Signal(object)
	sig_window_rect_changed    = QtCore.Signal(object)
	sig_was_iconic_changed     = QtCore.Signal(object)
	sig_bin_appearance_toggled = QtCore.Signal(object)
	sig_system_appearance_toggled = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._use_bin_appearance = True

		self.sig_bin_appearance_toggled.connect(lambda use_bin: self.sig_system_appearance_toggled.emit(not use_bin))

	@QtCore.Slot(object, object, object, object, object, object, object)
	def setAppearanceSettings(self,
		bin_font:str|int,
		mac_font_size:int,
		foreground_color:list[int],
		background_color:list[int],
		column_widths:dict[str,int],
		window_rect:list[int],
		was_iconic:bool
	):
		
		font = QtWidgets.QApplication.font()
		
		# JUST A NOTE:
		# I could be wrong, but I have a suspicion that these mac_* properties are 
		# specifically for frame view even though mac_font_size seems global
		font.setPixelSize(mac_font_size)

		if isinstance(bin_font, str) and QtGui.QFontDatabase.hasFamily(bin_font):
			font.setFamily(bin_font)

		# NOTE: mac_font int not a font index, at least not one we can make use of
		#elif isinstance(bin_font, int) and len(QtGui.QFontDatabase.families()) > bin_font:
		#	font.setFamily(QtGui.QFontDatabase.families()[bin_font])
		
		self.sig_font_changed.emit(font)
		
		self.setColumnWidths(column_widths)
		self.setWindowRect(window_rect)

		self.sig_was_iconic_changed.emit(was_iconic)
		self.sig_column_widths_changed.emit(column_widths)
		self.sig_palette_changed.emit(
			QtGui.QColor.fromRgba64(*foreground_color),
			QtGui.QColor.fromRgba64(*background_color),
		)

	@QtCore.Slot(QtGui.QColor, QtGui.QColor)
	def setBinColors(self, fg_color:QtGui.QColor, bg_color:QtGui.QColor):
		
		self.sig_palette_changed.emit(fg_color, bg_color)

	@QtCore.Slot(object)
	def setWindowRect(self, window_rect:list[int]):

		self.sig_window_rect_changed.emit(QtCore.QRect(
			QtCore.QPoint(*window_rect[:2]),
			QtCore.QPoint(*window_rect[2:])
		))

	
	@QtCore.Slot(object)
	def setColumnWidths(self, column_widths:dict[str,int]):
		"""Display column width settings"""

		self.viewModel().clear()

		for col, width in column_widths.items():
			self.addRow({
				self.tr("Width"):  width,
				self.tr("Column"): col,
			}, add_new_headers=True)
	
	@QtCore.Slot(object)
	def setEnableBinAppearance(self, is_enabled:bool):

		if not self._use_bin_appearance == is_enabled:
			self._use_bin_appearance = is_enabled
			self.sig_bin_appearance_toggled.emit(is_enabled)
	
	@QtCore.Slot(object)
	def setUseSystemAppearance(self, use_system:bool):

		self.setEnableBinAppearance(not use_system)
		


class BSBinSortingPropertiesManager(base.LBItemDefinitionView):
	"""Bin sorting"""

	sig_bin_sorting_changed   = QtCore.Signal(object)

	@QtCore.Slot(object)
	def setBinSortingProperties(self, sorting:list[int,str]):
		
		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order",     self.tr("Order")),
			viewmodelitems.LBAbstractViewHeaderItem("direction", self.tr("Direction")),
			viewmodelitems.LBAbstractViewHeaderItem("column",    self.tr("Column"))
		]

		for header in headers:
			self.addHeader(header)
		
		for order, (direction, column_name) in enumerate(sorting):
			self.addRow({
				"order": order,
				"direction": QtCore.Qt.SortOrder(direction),
				"column": column_name
			})
		
		self.sig_bin_sorting_changed.emit([(QtCore.Qt.SortOrder(direction), column_name) for direction, column_name in sorting])

class BSBinSiftSettingsManager(base.LBItemDefinitionView):

	sig_sift_enabled          = QtCore.Signal(bool)
	sig_bin_view_changed      = QtCore.Signal(object)
	sig_sift_settings_changed = QtCore.Signal(object)

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):
		self.sig_bin_view_changed.emit(bin_view)


	@QtCore.Slot(bool, object)
	def setSiftSettings(self, sift_enabled:bool, sift_settings:list[avbutils.bins.BinSiftOption]):

		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="string", display_name=self.tr("String")))
		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="method", display_name=self.tr("Method")))
		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="column", display_name=self.tr("Column")))
		for idx, setting in enumerate(reversed(sift_settings)):
			self.addRow({
				"order": idx,
				"method": viewmodelitems.TRTEnumViewItem(setting.sift_method),
				"string": setting.sift_text,
				"column": setting.sift_column,
			})
		
		self.sig_sift_settings_changed.emit(sift_settings)		
		self.sig_sift_enabled.emit(sift_enabled)

class BSBinItemsManager(base.LBItemDefinitionView):
	
	sig_mob_added = QtCore.Signal(object)
	"""A mob was added to the bin items"""

	sig_mob_count_changed = QtCore.Signal(int)
	"""Mobs were added or removed"""

	sig_bin_view_changed = QtCore.Signal(object, object)

	def __init__(self):

		super().__init__()

		self._frame_scene = QtWidgets.QGraphicsScene()
		
		self._view_model.rowsInserted .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
		self._view_model.rowsRemoved  .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
		self._view_model.modelReset   .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))

	@QtCore.Slot(object, object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict[str,int]):

		self.viewModel().clear()
		self.frameScene().clear()

		for column in bin_view.columns:

			self.addHeader(
				viewmodelitems.LBAbstractViewHeaderItem(
					field_name="40_"+column["title"] if column["type"] == 40 else str(column["type"]),
					field_id=column["type"],
					format_id=column["format"],
					display_name=column["title"],
					is_hidden=column["hidden"],
					field_width=column_widths.get(column["title"])
				)
			)
		
		self.sig_bin_view_changed.emit(bin_view, column_widths)
	
	@QtCore.Slot(object)
	def addMob(self, mob_info:binparser.BinItemInfo):

		self.addRow(mob_info.column_data)
		#print(mob_info.coordinates)
		
		#self._frame_scale = 11
		self._frame_scale = 1
		
		TEMP_POSITION_OFFSET_THING = 10

		item_rect = BSFrameModeItem()
		item_rect.setPos(mob_info.coordinates[0]/TEMP_POSITION_OFFSET_THING, mob_info.coordinates[1]/TEMP_POSITION_OFFSET_THING)
		item_rect.setScale(self._frame_scale)
		item_rect.setName(mob_info.column_data.get(avbutils.BIN_COLUMN_ROLES.get("Name")))
		item_rect.setClipColor(mob_info.column_data.get(avbutils.BIN_COLUMN_ROLES.get("Color")).raw_data())
		item_rect.setSelected(True)
		item_rect.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable|QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

		
		self._frame_scene.addItem(
			item_rect
		)

		#self.sig_mob_added.emit(mob_info)
	
	@QtCore.Slot(object)
	def addMobs(self, mob_info_list:list[binparser.BinItemInfo]):

		self.addRows([m.column_data for m in mob_info_list])

		for mob_info in mob_info_list:
			
			self._frame_scale = 1
		
			

			item_rect = BSFrameModeItem()
			item_rect.setPos(mob_info.coordinates[0]/TEMP_POSITION_OFFSET_THING, mob_info.coordinates[1]/TEMP_POSITION_OFFSET_THING)
			item_rect.setScale(self._frame_scale)
			item_rect.setName(mob_info.column_data.get(avbutils.BIN_COLUMN_ROLES.get("Name")))
			item_rect.setClipColor(mob_info.column_data.get(avbutils.BIN_COLUMN_ROLES.get("Color")).raw_data())
			item_rect.setSelected(True)
			item_rect.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable|QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

			
			self._frame_scene.addItem(
				item_rect
			)



		#self.sig_mob_added.emit(mob_info_list)

		# ALSO Add Frame Items

	def frameScene(self) -> QtWidgets.QGraphicsScene:
		return self._frame_scene
	
class BSFrameModeItem(QtWidgets.QGraphicsItem):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._clip_color = QtGui.QColor()

	def boundingRect(self) -> QtCore.QRectF:
		return QtCore.QRectF(QtCore.QPoint(0,0),QtCore.QSize(18,12))
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionGraphicsItem, /,	 widget:QtWidgets.QWidget = ...):

		painter.save()

		pen = QtGui.QPen()
		pen.setWidth(4)
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
		pen.setCosmetic(True)

		brush = QtGui.QBrush()
		brush.setColor(option.palette.color(QtGui.QPalette.ColorRole.Dark))
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(self.boundingRect())

		brush = QtGui.QBrush()
		brush.setColor(option.palette.color(QtGui.QPalette.ColorRole.Button))
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		pen = QtGui.QPen()
		pen.setStyle(QtCore.Qt.PenStyle.NoPen)
		

		painter.setBrush(brush)
		painter.setPen(pen)

		clip_preview_rect = self.boundingRect().adjusted(0, 0, 0, -1).adjusted(.5,.5,-.5,-.5)

		painter.drawRect(clip_preview_rect)

		if self._clip_color.isValid():
			#pass

			pen = QtGui.QPen()
			pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
			pen.setWidthF(0.25/self.scale())
			pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
			pen.setColor(self._clip_color)
			
			brush = QtGui.QBrush()
			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)

			painter.setPen(pen)
			painter.setBrush(brush)
			painter.drawRect(self.boundingRect().adjusted(.25,.25,-.25,-.25))

		font = QtWidgets.QApplication.font()
		font.setPixelSize(1/self.scale())
		
		painter.setFont(font)
		pen = QtGui.QPen()
		painter.setPen(pen)
		painter.drawText(self.boundingRect().adjusted(0.25,0.25,-0.25,-0.25), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignBottom, self._name)

		painter.drawText(QtCore.QPoint(0,0) + QtCore.QPoint(0,1), f"({self.pos().x():.1f},{self.pos().y():.1f})")
		
		if self.isSelected():
			brush = QtGui.QBrush()
			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
			color_highlight:QtGui.QColor = option.palette.color(QtGui.QPalette.ColorRole.Highlight)
			color_highlight.setAlphaF(0.5)
			brush.setColor(color_highlight)

			pen = QtGui.QPen()
			pen.setStyle(QtCore.Qt.PenStyle.NoPen)

			painter.setBrush(brush)
			painter.setPen(pen)
			painter.drawRect(self.boundingRect())

		
		painter.restore()

	def setName(self, name:str):
		self._name = name
	
	def setClipColor(self, color:QtGui.QColor):

		self._clip_color = color