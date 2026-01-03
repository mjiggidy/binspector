"""
Manage display delegates
"""

from ..core.config import BSListViewConfig
from . import binitems
import avbutils
from PySide6 import QtCore

ITEM_DELEGATES_PER_FIELD_ID = {
	51 : binitems.BSIconLookupItemDelegate(aspect_ratio=QtCore.QSize(4,3), padding=BSListViewConfig.DEFAULT_ITEM_PADDING), # Clip color
	132: binitems.BSIconLookupItemDelegate(aspect_ratio=QtCore.QSize(4,3), padding=BSListViewConfig.DEFAULT_ITEM_PADDING), # Marker
	200: binitems.BSIconLookupItemDelegate(aspect_ratio=QtCore.QSize(4,3), padding=BSListViewConfig.DEFAULT_ITEM_PADDING), # Bin Display Item Type

}
"""Specialized one-off fields"""

ITEM_DELEGATES_PER_FORMAT_ID = {
	avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate(padding=BSListViewConfig.DEFAULT_ITEM_PADDING),
}
"""Delegate for generic field formats"""