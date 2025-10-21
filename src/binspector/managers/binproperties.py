import avb, avbutils
from PySide6 import QtCore, QtGui, QtWidgets
from ..models import viewmodelitems
from ..core import binparser
from . import base

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

	sig_bin_view_changed = QtCore.Signal(object, object)
	"""Binview has been reset"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting, column_widths:dict|None=None):
		"""Set columns and their widths"""

		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order", "Order"),
			viewmodelitems.LBAbstractViewHeaderItem("title", "Title"),
			viewmodelitems.LBAbstractViewHeaderItem("format", "Format"),
			viewmodelitems.LBAbstractViewHeaderItem("type", "Type"),
			viewmodelitems.LBAbstractViewHeaderItem("width", "Width"),
			viewmodelitems.LBAbstractViewHeaderItem("hidden", "Is Hidden"),
		]
		
		for header in headers[::-1]:
			super().addHeader(header)

		for idx, column in enumerate(bin_view.columns):
			column.update({
				"order": idx,
				"width": column_widths.get(column["title"],None)
			})
				
			self.addColumnDefinition(column)
		
		self.sig_bin_view_changed.emit(bin_view, column_widths)

	@QtCore.Slot(object)
	def addColumnDefinition(self, column_definition:dict[str,object]):

		column_definition["format"] = avbutils.BinColumnFormat(column_definition["format"])
		self.addRow(column_definition)

class BSBinDisplaySettingsManager(base.LBItemDefinitionView):

	sig_bin_display_changed = QtCore.Signal(object)

	def __init__(self):

		super().__init__()

	@QtCore.Slot(object)
	def setBinDisplayFlags(self, bin_display:avbutils.BinDisplayItemTypes):

		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("name", "Name"),
			viewmodelitems.LBAbstractViewHeaderItem("value", "Value"),
		]
		
		for header in headers[::-1]:
			self.addHeader(header)
		
		for f in bin_display:
			self.addRow({"name": f.name, "value": f.value})
		
		self.sig_bin_display_changed.emit(bin_display)
		
class BSBinAppearanceSettingsManager(base.LBItemDefinitionView):

	sig_font_changed          = QtCore.Signal(QtGui.QFont)
	sig_palette_changed       = QtCore.Signal(QtGui.QColor, QtGui.QColor)
	sig_column_widths_changed = QtCore.Signal(object)
	sig_window_rect_changed   = QtCore.Signal(object)
	sig_was_iconic_changed    = QtCore.Signal(bool)

	@QtCore.Slot(object, object, object, object, object, object, object)
	def setAppearanceSettings(self,
		bin_font:str|int,
		mac_font_size:int,
		foreground_color:list[int],
		background_color:list[int],
		column_widths:dict[str,int],
		window_rect:list[int],
		was_iconic:bool):
		
		font = QtGui.QFont()
		font.setPixelSize(mac_font_size)

		if isinstance(bin_font, str) and QtGui.QFontDatabase.hasFamily(bin_font):
			font.setFamily(bin_font)

		elif isinstance(bin_font, int) and len(QtGui.QFontDatabase.families()) > bin_font:
			font.setFamily(QtGui.QFontDatabase.families()[bin_font])
		
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
				"Width":  width,
				"Column": col,
			}, add_new_headers=True)

class BSBinSortingPropertiesManager(base.LBItemDefinitionView):
	"""Bin sorting"""

	sig_bin_sorting_changed = QtCore.Signal(object)

	@QtCore.Slot(object)
	def setBinSortingProperties(self, sorting:list[int,str]):
		
		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order", "Order"),
			viewmodelitems.LBAbstractViewHeaderItem("direction", "Direction"),
			viewmodelitems.LBAbstractViewHeaderItem("column", "Column")
		]

		for header in headers[::-1]:
			self.addHeader(header)
		
		for order, (direction, column_name) in enumerate(sorting):
			self.addRow({
				"order": order,
				"direction": QtCore.Qt.SortOrder(direction),
				"column": column_name
			})
		
		self.sig_bin_sorting_changed.emit([(QtCore.Qt.SortOrder(direction), column_name) for direction, column_name in sorting])

class BSBinSiftSettingsManager(base.LBItemDefinitionView):

	sig_sift_enabled = QtCore.Signal(bool)

	@QtCore.Slot(bool, object)
	def setSiftSettings(self, sift_enabled:bool, sift_settings:list[avb.bin.SiftItem]):

		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="string", display_name="String"))
		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="method", display_name="Method"))
		self.addHeader(viewmodelitems.LBAbstractViewHeaderItem(field_name="column", display_name="Column"))
		for idx, setting in enumerate(sift_settings):
			self.addRow({
				"order": idx,
				"method": viewmodelitems.TRTEnumViewItem(avbutils.BinSiftMethod(setting.method)),
				"string": setting.string,
				"column": setting.column,
			})
		
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

		for column in bin_view.columns[::-1]:

#			if column["hidden"]:
#				continue

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
	
		#print(item_rect.flags())
		
		
		self._frame_scene.addItem(
			item_rect
		)


		self.sig_mob_added.emit(mob_info)

	def frameScene(self) -> QtWidgets.QGraphicsScene:
		return self._frame_scene
	
class BSFrameModeItem(QtWidgets.QGraphicsItem):

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
			pass

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

		font = QtGui.QFont()
		font.setPixelSize(1/self.scale())
		
		painter.setFont(font)
		pen = QtGui.QPen()
		painter.setPen(pen)
		painter.drawText(self.boundingRect().adjusted(0.25,0.25,-0.25,-0.25), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignBottom, self._name)

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