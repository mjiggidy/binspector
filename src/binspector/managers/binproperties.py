import avb, avbutils
from PySide6 import QtCore, QtGui
from ..models import viewmodelitems
from . import base

class BSBinViewManager(base.LBItemDefinitionView):

	sig_bin_view_changed = QtCore.Signal(object)
	"""Binview has been reset"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):
		self.viewModel().clear()

		headers = [
			viewmodelitems.LBAbstractViewHeaderItem("order", "Order"),
			viewmodelitems.LBAbstractViewHeaderItem("title", "Title"),
			viewmodelitems.LBAbstractViewHeaderItem("format", "Format"),
			viewmodelitems.LBAbstractViewHeaderItem("type", "Type"),
			viewmodelitems.LBAbstractViewHeaderItem("hidden", "Is Hidden"),
		]
		
		for header in headers[::-1]:
			super().addHeader(header)

		for idx, column in enumerate(bin_view.columns):
			column.update({"order": idx})
			self.addColumnDefinition(column)
		
		self.sig_bin_view_changed.emit(bin_view)

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

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):

		self.viewModel().clear()

		for column in bin_view.columns[::-1]:

			if column["hidden"]:
				continue

			self.addHeader(
				viewmodelitems.LBAbstractViewHeaderItem(
					field_name="40_"+column["title"] if column["type"] == 40 else str(column["type"]),
					field_id=column["type"],
					format_id=column["format"],
					display_name=column["title"],
				)
			)
	
	@QtCore.Slot(object)
	def addMob(self, mob_info:dict):

		self.addRow(mob_info)
		self.sig_mob_added.emit(mob_info)