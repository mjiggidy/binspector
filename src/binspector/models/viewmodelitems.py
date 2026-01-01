import typing, enum, datetime, os
import avbutils
from timecode import Timecode
from PySide6 import QtCore, QtGui, QtWidgets
from functools import singledispatch


class LBAbstractViewHeaderItem:
	"""An abstract header item for TRT views"""

	def __init__(self,
			  field_name:str,
			  display_name:str,
			  field_id:int=0,
			  format_id:int=0,
			  is_hidden:bool=False,
			  icon:QtGui.QIcon|None=None,
			  item_factory:typing.Type["LBAbstractViewItem"]|None=None, 
			  delegate:QtWidgets.QStyledItemDelegate|None=None,
			  field_width:int|None=None,
		):

		self._field_name   = field_name
		self._field_id     = field_id # Think I wanna do this for bin headings
		self._field_width  = field_width
		self._format_id    = format_id
		self._display_name = display_name
		self._is_hidden    = is_hidden


		self._item_factory = item_factory
		self._icon = icon

		self._delgate = delegate

		self._data_roles = {}
		self._prepare_data()
	
	def _prepare_data(self):
		"""Precalculate Header Data"""

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: str(self._display_name),
			QtCore.Qt.ItemDataRole.DecorationRole: self._icon,
			QtCore.Qt.ItemDataRole.UserRole:    self,
			QtCore.Qt.ItemDataRole.UserRole+1:  self._field_id, # Think I wanna do this for bin headings
			QtCore.Qt.ItemDataRole.UserRole+2:  self._format_id,
			QtCore.Qt.ItemDataRole.UserRole+3:  self._is_hidden,
			QtCore.Qt.ItemDataRole.UserRole+4:  self._field_width,
			QtCore.Qt.ItemDataRole.UserRole+5:  self._field_name,
		 })
	
	def data(self, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		return self._data_roles.get(role, None)
	
	def itemData(self) -> dict[QtCore.Qt.ItemDataRole, typing.Any]:
		return self._data_roles
	
	def item_factory(self) -> typing.Type:
		return self._item_factory
	
	def field_name(self) -> str:
		return self._field_name
	
	def format_id(self) -> avbutils.BinColumnFormat:
		return avbutils.BinColumnFormat(self._format_id)
	
	def field_width(self) -> int|None:
		return self._field_width
	
	def display_name(self) -> str:
		return self._display_name
	
	def delegate(self) -> QtWidgets.QStyledItemDelegate:
		return self._delgate
	
	def isHidden(self) -> bool:
		return self._is_hidden

class LBAbstractViewItem:
	"""An abstract item for TRT views"""

	def __init__(self, raw_data:typing.Any, icon:QtGui.QIcon|None=None, tooltip:QtWidgets.QToolTip|str|None=None):

		self._data = raw_data
		self._icon = icon
		self._tooltip = tooltip

		self._data_roles = {}
		self._prepare_data()
	
	def _prepare_data(self):
		"""Precalculate them datas for all them roles"""
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self.to_string(self._data),
			QtCore.Qt.ItemDataRole.ToolTipRole:          self._tooltip if self._tooltip is not None else repr(self._data),
			QtCore.Qt.ItemDataRole.DecorationRole:       self._icon,
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self.to_string(self._data),	# QCollator just compares strings
			QtCore.Qt.ItemDataRole.TextAlignmentRole:    QtCore.Qt.AlignmentFlag.AlignTop,
			QtCore.Qt.ItemDataRole.UserRole:             self,
		})
	def raw_data(self) -> typing.Any:
		"""Get the original data for this item in its original format"""
		return self._data

	def data(self, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		"""Get item data for a given role.  By default, returns the raw data as a string."""
		return self._data_roles.get(role, None)
	
	def setData(self, role:QtCore.Qt.ItemDataRole, data:typing.Any):
		"""Override data for a particular role"""
		self._data_roles[role] = data
	
	def itemData(self) -> dict[QtCore.Qt.ItemDataRole, typing.Any]:
		"""Get all item data roles"""
		return self._data_roles
	
	def to_json(self) -> str:
		"""Format as JSON object"""
		return self.data(QtCore.Qt.ItemDataRole.DisplayRole)
	
	@classmethod
	def to_string(cls, data:typing.Any) -> str:
		return str(data)
	
class TRTStringViewItem(LBAbstractViewItem):
	"""A standard string"""

	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: self.to_string(self._data),
		})

class TRTEnumViewItem(LBAbstractViewItem):
	"""Represents an Enum"""

	def __init__(self, raw_data:enum.Enum, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DecorationRole:       self._data,
			QtCore.Qt.ItemDataRole.DisplayRole:          self._data.name.replace("_", " ").title(),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self.to_string(self._data.value),
		})
	

class TRTNumericViewItem(LBAbstractViewItem):
	"""A numeric value"""

	STRING_PADDING:int = 0
	"""Left-side padding for string formatting"""

	def __init__(self, raw_data:int, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self.to_string(self._data),
			#QtCore.Qt.ItemDataRole.InitialSortOrderRole: self._data,
			QtCore.Qt.ItemDataRole.FontRole:             QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont).family(),
			QtCore.Qt.ItemDataRole.TextAlignmentRole:    QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTop,
		})
	
	def to_json(self) -> int:
		return self.data(QtCore.Qt.ItemDataRole.UserRole) # NOTE to self: need to change this to access item's _data
	
	@classmethod
	def to_string(cls, data):
		return super().to_string(data).rjust(cls.STRING_PADDING)

class TRTPathViewItem(LBAbstractViewItem):
	"""A file path"""

	def __init__(self, raw_data:str|QtCore.QFileInfo):
		super().__init__(QtCore.QFileInfo(raw_data))
	
	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self._data.fileName(),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self._data.fileName(),
			QtCore.Qt.ItemDataRole.DecorationRole:       QtWidgets.QFileIconProvider().icon(self._data),
			QtCore.Qt.ItemDataRole.ToolTipRole:          QtCore.QDir.toNativeSeparators(self._data.absoluteFilePath()),
		})
	
	def to_json(self) -> str:
		return QtCore.QDir.toNativeSeparators(self.data(QtCore.Qt.ItemDataRole.UserRole).absoluteFilePath())

class TRTDateTimeViewItem(LBAbstractViewItem):
	"""A datetime entry"""

	def __init__(self, raw_data:datetime.datetime, format_string:QtCore.Qt.DateFormat|str=QtCore.Qt.DateFormat.TextDate):
		
		self._format_string = format_string
		
		super().__init__(QtCore.QDateTime(raw_data).toLocalTime())
	
	def setFormatString(self, format_string:str):
		"""Set the datetime formatting string used by strftime"""
		self._format_string = format_string
		self._data_roles.update()
	
	def formatString(self) -> str:
		"""The datetime formatting string used by strftime"""
		return self._format_string

	def _prepare_data(self):
		super()._prepare_data()
	
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self._data.toString(self._format_string),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: str(self._data.toMSecsSinceEpoch()),
			QtCore.Qt.ItemDataRole.TextAlignmentRole:    QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTop,
		})
	
	def to_json(self) -> dict:
		return {
			"type": "datetime",
			"timestamp": self.data(QtCore.Qt.ItemDataRole.UserRole).timestamp(),
			"formatted": self.data(QtCore.Qt.ItemDataRole.DisplayRole)
		}

class TRTTimecodeViewItem(TRTNumericViewItem):
	"""A timecode"""

	def __init__(self, raw_data:Timecode, *args, **kwargs):
		if not isinstance(raw_data, Timecode):
			raise TypeError("Data must be an instance of `Timecode`")
		super().__init__(raw_data, *args, **kwargs)
	
	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: str(self._data.frame_number),
		})
	
	def to_json(self) -> dict:
		tc = self.data(QtCore.Qt.ItemDataRole.UserRole)
		return {
			"type": "timecode",
			"frames": tc.frame_number,
			"rate": tc.rate,
			"formatted": self.data(QtCore.Qt.ItemDataRole.DisplayRole).strip()
		}

class TRTDurationViewItem(TRTTimecodeViewItem):
	"""A duration (hh:mm:ss:ff), a subset of timecode"""

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: self.to_string(self._data),
		})
	
	@classmethod
	def to_string(cls, data):

		tc_str = str(data)
		is_neg =tc_str.startswith("-")
		
		# Get the index of the last separator
		leading_chars = 1
		sep = ":"
		idx_last_sep = tc_str.rfind(sep) - leading_chars
		pre, post = tc_str[:idx_last_sep], tc_str[idx_last_sep:]
		pre = pre.lstrip("-00" + sep)

		return f"{'-' if is_neg else ''}{pre}{post}".rjust(cls.STRING_PADDING)

class TRTFeetFramesViewItem(TRTNumericViewItem):
	"""A frame offset described in feet & frames (f+ff)"""

	def __init__(self, raw_data:int, *args, **kwargs):

		if not isinstance(raw_data, int):
			raise TypeError(f"Data must be an integer (not {type(raw_data)})")
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()
	
	def to_json(self) -> dict:
		return {
			"type":      "feet_frames",
			"format":    "35mm",
			"perfs":     4,
			"frames":    self.data(QtCore.Qt.ItemDataRole.UserRole),
			"formatted": self.data(QtCore.Qt.ItemDataRole.DisplayRole).strip()
		}
	
	@classmethod
	def to_string(cls, data):
		return str(str(data // 16) + "+" + str(data % 16).zfill(2)).rjust(cls.STRING_PADDING)

class TRTClipColorViewItem(LBAbstractViewItem):
	"""A clip color"""

	def __init__(self, raw_data:avbutils.ClipColor|QtGui.QRgba64|None, *args, **kwargs):

		if isinstance(raw_data, avbutils.ClipColor):
			raw_data = QtGui.QColor.fromRgba64(*raw_data.as_rgb16())
		elif isinstance(raw_data, QtGui.QRgba64):
			raw_data = QtGui.QColor.fromRgba64(raw_data)
		elif raw_data is None:
			raw_data = QtGui.QColor()
		elif not isinstance(raw_data, QtGui.QColor):
			raise TypeError(f"Data must be a QColor object (got {type(raw_data)})")
		
		super().__init__(raw_data, *args, **kwargs)
	
	def _prepare_data(self):
		# Not calling super, would be weird

		self._data_roles.update({
			#QtCore.Qt.ItemDataRole.UserRole: self._data,
			#QtCore.Qt.ItemDataRole.BackgroundRole: self._data,
			QtCore.Qt.ItemDataRole.DecorationRole: self._data.toTuple() if self._data.isValid() else -1,
			QtCore.Qt.ItemDataRole.ToolTipRole: f"R: {self._data.red()} G: {self._data.green()} B: {self._data.blue()}" if self._data.isValid() else "No Color",
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self.to_string(self._data.getRgb())
		})
	
	def to_json(self) -> dict|None:

		color = self.raw_data()
		
		if not color.isValid():
			return None
		
		color_64 = color.rgba64()

		return {
			"type": "color",
			"rgb16": [color_64.red(), color_64.green(), color_64.blue()],
			"rgb8": [color.red(), color.green(), color.blue()],
			"hex": self.data(QtCore.Qt.ItemDataRole.UserRole).name()
		}

class TRTMarkerViewItem(LBAbstractViewItem):
	"""Marker column"""

	def __init__(self, raw_data:avbutils.MarkerInfo, *args, **kwargs):

		super().__init__(raw_data, *args, **kwargs)
		self._prepare_data()
	
	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: None,
			QtCore.Qt.ItemDataRole.DecorationRole: QtGui.QColor(self._data.color.name).toTuple() if self._data.color else -1,
			#QtCore.Qt.ItemDataRole.UserRole: QtGui.QColor(self._data.color.name),
		})

class TRTBinLockViewItem(LBAbstractViewItem):
	"""Bin lock info"""

	# Note: For now I think we'll do a string, but want to expand this later probably
	def __init__(self, raw_data:avbutils.LockInfo, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:    self._data.name if self._data else "",
			QtCore.Qt.ItemDataRole.DecorationRole: QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SystemLockScreen if self._data else None)
		})
	
	def to_json(self) -> str|None:
		return self.data(QtCore.Qt.ItemDataRole.DisplayRole) or None

@singledispatch
def get_viewitem_for_item(item:typing.Any) -> LBAbstractViewItem:
	"""Return the most suitable view item for a given item"""
	return TRTStringViewItem(item)

@get_viewitem_for_item.register
def _(item:LBAbstractViewItem):
	return item

@get_viewitem_for_item.register
def _(item:str):
	return TRTStringViewItem(item)

@get_viewitem_for_item.register
def _(item:int|float):
	return TRTNumericViewItem(item)

@get_viewitem_for_item.register
def _(item:enum.Enum):
	return TRTEnumViewItem(item)

@get_viewitem_for_item.register
def _(item:os.PathLike):
	return TRTPathViewItem(item)

@get_viewitem_for_item.register
def _(item:str):
	return TRTStringViewItem(item)

@get_viewitem_for_item.register
def _(item:datetime.datetime):
	return TRTDateTimeViewItem(item)

@get_viewitem_for_item.register
def _(item:Timecode):
	return TRTTimecodeViewItem(item)