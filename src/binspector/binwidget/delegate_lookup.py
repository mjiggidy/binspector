"""
Manage display delegates
"""

from ..core.config import BSListViewConfig
from . import binitems
import avbutils
from PySide6 import QtCore

ITEM_DELEGATES_PER_FIELD_ID = {
	51 : binitems.BSIconLookupItemDelegate, # Clip color
	132: binitems.BSIconLookupItemDelegate, # Marker
	200: binitems.BSIconLookupItemDelegate, # Bin Display Item Type

}
"""Specialized one-off fields"""

ITEM_DELEGATES_PER_FORMAT_ID = {
	avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate,
}
"""Delegate for generic field formats"""