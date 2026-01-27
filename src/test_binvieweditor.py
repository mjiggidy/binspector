from __future__ import annotations
import sys, enum, typing, os, dataclasses
import avb, avbutils
from PySide6 import QtCore, QtWidgets

from binspector.models import viewmodelitems

class BSBinViewModel(QtCore.QAbstractItemModel):

	class BSBinViewEditorColumns(enum.IntEnum):

		POSITION    = enum.auto()
		NAME        = enum.auto()
		DATA_FORMAT = enum.auto()
		DELETE      = enum.auto()
		VISIBILITY  = enum.auto()

	def __init__(self, *args, items:list[viewmodelitems.LBAbstractViewHeaderItem]|None=None, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._bin_view_columns:list[viewmodelitems.LBAbstractViewHeaderItem] = items or list()

	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:

		return QtCore.QModelIndex()
	
	def rowCount(self, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return 0

		return len(self._bin_view_columns)
	
	def columnCount(self, parent:QtCore.QModelIndex) -> int:

		return 1
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:

		
		if not index.isValid():
			return None
		
		return self._bin_view_columns[index.row()].data(role)

	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if parent.isValid():
			return QtCore.QModelIndex()

		return self.createIndex(row, column, None)


@dataclasses.dataclass(frozen=True)
class BSBinViewColumnInfo:

	name      :str
	field_id  :avbutils.bins.BinColumnFieldIDs
	format_id :avbutils.bins.BinColumnFormat
	is_hidden :bool
	width     :int

	@classmethod
	def from_column(cls, column_info:dict, width:int|None=None):

		if column_info["type"] not in avbutils.bins.BinColumnFieldIDs:
			raise ValueError(f"Unknown field ID: {column_info['type']}")
		
		elif column_info["format"] not in avbutils.bins.BinColumnFormat:
			raise ValueError(f"Unknown column format ID: {column_info['format']}")

		return cls(
			name = column_info["title"],
			field_id = avbutils.bins.BinColumnFieldIDs(column_info["type"]),
			format_id = avbutils.bins.BinColumnFormat(column_info["format"]),
			is_hidden = column_info["hidden"],
			width = width
		)
	
@dataclasses.dataclass(frozen=True)
class BSBinViewInfo:

	name:str
	columns:list[BSBinViewColumnInfo]

	@classmethod
	def from_binview(cls, binview:avb.bin.BinViewSetting) -> typing.Self:

		cols = list()

		for column in binview.columns:
			
			try:
				cols.append(BSBinViewColumnInfo.from_column(column))
			except ValueError as e:
				print(e)
				continue
		
		return cls(
			binview.name,
			cols
		)

def get_binview(bin_path:os.PathLike[str]) -> BSBinViewInfo:



	with avb.open(bin_path) as bin_handle:

		bin_contents = bin_handle.content
		bin_view     = bin_contents.view_setting

		return BSBinViewInfo.from_binview(bin_view)
	
	
def main(bin_path:os.PathLike[str]):

	app = QtWidgets.QApplication()
	
	binview_info = get_binview(bin_path)

	binview_col_views = []

	for col in binview_info.columns:

		col_view = viewmodelitems.LBAbstractViewHeaderItem(
			field_name=str(col.field_id.value) + "_" + col.name,
			display_name=col.name,
			field_id = col.field_id,
			format_id=col.format_id,
			is_hidden=col.is_hidden
		)

		binview_col_views.append(col_view)

	model_binview = BSBinViewModel(items=binview_col_views)

	columns_list = QtWidgets.QListView()
	columns_list.setAlternatingRowColors(True)
	columns_list.setModel(model_binview)
	columns_list.show()

	
	return app.exec()
	
if __name__ == "__main__":

	if not len(sys.argv) > 1:
	
		import pathlib
		sys.exit(f"Usage: {pathlib.Path(__file__).name} bin_path.avb")
	
	sys.exit(main(sys.argv[1]))