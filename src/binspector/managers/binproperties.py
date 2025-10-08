import avb, avbutils
from PySide6 import QtCore, QtGui
from ..models import viewmodelitems
from . import base

class BSBinViewManager(base.LBItemDefinitionView):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):
		self.viewModel().clear()

		headers = [
			viewmodelitems.TRTAbstractViewHeaderItem("order", "Order"),
			viewmodelitems.TRTAbstractViewHeaderItem("title", "Title"),
			viewmodelitems.TRTAbstractViewHeaderItem("format", "Format"),
			viewmodelitems.TRTAbstractViewHeaderItem("type", "Type"),
			viewmodelitems.TRTAbstractViewHeaderItem("hidden", "Is Hidden"),
		]
		
		for header in headers[::-1]:
			super().addHeader(header)

		for idx, column in enumerate(bin_view.columns):
			column.update({"order": idx})
			self.addColumnDefinition(column)

	@QtCore.Slot(object)
	def addColumnDefinition(self, column_definition:dict[str,object]):

		column_definition["format"] = avbutils.BinColumnFormat(column_definition["format"])
		self.addRow(column_definition)

class LBBinViewPropertyDataManager(base.LBItemDefinitionView):

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):

		self.viewModel().clear()

		headers = [
			viewmodelitems.TRTAbstractViewHeaderItem("name", "Name"),
			viewmodelitems.TRTAbstractViewHeaderItem("value", "Value"),
		]
		
		for header in headers[::-1]:
			self.addHeader(header)
		
		for key,val in bin_view.property_data.items():
			self.addRow({"name": key, "value": val})

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

		if isinstance(bin_font, str) and QtGui.QFontDatabase.hasFamily(bin_font):
			font.setFamily(bin_font)

		elif isinstance(bin_font, int) and len(QtGui.QFontDatabase.families()) > bin_font:
			font.setFamily(QtGui.QFontDatabase.families()[bin_font])
		
		font.setPixelSize(mac_font_size)

		self.setColumnWidths(column_widths)
		self.setWindowRect(window_rect)
		self.sig_was_iconic_changed.emit(was_iconic)
		self.sig_column_widths_changed.emit(column_widths)
		self.sig_font_changed.emit(font)
		self.sig_palette_changed.emit(
			QtGui.QColor.fromRgba64(*foreground_color),
			QtGui.QColor.fromRgba64(*background_color),
		)


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
			viewmodelitems.TRTAbstractViewHeaderItem("order", "Order"),
			viewmodelitems.TRTAbstractViewHeaderItem("direction", "Direction"),
			viewmodelitems.TRTAbstractViewHeaderItem("column", "Column")
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
		self.sig_sift_enabled.emit(sift_enabled)

		self.addHeader(viewmodelitems.TRTAbstractViewHeaderItem(field_name="string", display_name="String"))
		self.addHeader(viewmodelitems.TRTAbstractViewHeaderItem(field_name="method", display_name="Method"))
		self.addHeader(viewmodelitems.TRTAbstractViewHeaderItem(field_name="column", display_name="Column"))
		for idx, setting in enumerate(sift_settings):
			self.addRow({
				"order": idx,
				"method": viewmodelitems.TRTEnumViewItem(avbutils.BinSiftMethod(setting.method)),
				"string": setting.string,
				"column": setting.column,
			})

class BSBinItemsManager(base.LBItemDefinitionView):

	@QtCore.Slot(object)
	def setBinView(self, bin_view:avb.bin.BinViewSetting):

		self.viewModel().clear()

		for column in bin_view.columns[::-1]:

			if column["hidden"]:
				continue

			self.addHeader(
				viewmodelitems.TRTAbstractViewHeaderItem(
					field_name="40_"+column["title"] if column["type"] == 40 else str(column["type"]),
					field_id=column["type"],
					format_id=column["format"],
					display_name=column["title"],
				)
			)
	
	@QtCore.Slot(object)
	def addMob(self, mob_info:dict):
		self.addRow(mob_info)