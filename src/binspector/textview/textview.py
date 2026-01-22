from __future__ import annotations
import logging, enum, typing
from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSTextViewModeConfig
from ..models import viewmodels
from ..views  import treeview
from ..utils import columnselect
from ..res import icons_binitems
from . import proxydelegates
from ..binwidget import itemdelegates
from ..core import icon_providers
from .proxydelegates import FieldLookupDict, FormatLookupDict

if typing.TYPE_CHECKING:
	import avbutils
	from os import PathLike

type IconRegistryType = dict[avbutils.bins.BinDisplayItemTypes, PathLike[str]]

class BSBinTextView(treeview.BSTreeViewBase):
	"""QTreeView but nicer"""

	sig_default_sort_columns_changed = QtCore.Signal(object)
	"""TODO: HMMMMMM"""

	sig_selection_model_changed      = QtCore.Signal(object)
	"""Selection model was changed"""

	sig_item_padding_changed         = QtCore.Signal(object)


	def __init__(self, *args, bin_item_icon_registry:IconRegistryType|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.ICON_ASPECT_RATIO = QtCore.QSizeF(4,3)

		self.setModel(viewmodels.BSBinViewProxyModel())
		self.setSelectionBehavior(BSTextViewModeConfig.DEFAULT_SELECTION_BEHAVIOR)
		self.setSelectionMode(BSTextViewModeConfig.DEFAULT_SELECTION_MODE)

		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.setDropIndicatorShown(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

		self._bin_item_icon_registry = bin_item_icon_registry or dict()
		self._delegate_provider      = proxydelegates.BSBinColumnDelegateProvider(view=self)
		self._proxy_delegate         = proxydelegates.BSBinColumnProxyDelegate(delegate_provider=self._delegate_provider)

		self.registerCustomDelegates()
		self.setItemDelegate(self._proxy_delegate)

		self._column_select_watcher = columnselect.BSColumnSelectWatcher(parent=self)
		self._column_select_watcher.sig_column_selected.connect(self.selectSectionFromCoordinates)
		self.header().viewport().installEventFilter(self._column_select_watcher)
		
		self._item_padding          = QtCore.QMarginsF(BSTextViewModeConfig.DEFAULT_ITEM_PADDING)
		self.setItemPadding(self._item_padding)


	def setBinItemIconRegistry(self, registry:IconRegistryType):
		"""Register bin item icon paths"""

		if self._bin_item_icon_registry == registry:
			return
		
		self._bin_item_icon_registry = registry
		
		self.registerCustomDelegates()
#
	def setSelectionModel(self, selectionModel):

		if selectionModel == self.selectionModel():
			return

		logging.getLogger(__name__).error("BinTreeView changed selection model to %s", str(selectionModel))
		self.sig_selection_model_changed.emit(selectionModel)

		return super().setSelectionModel(selectionModel)

	@QtCore.Slot(object)
	def setModel(self, model:viewmodels.BSBinViewProxyModel):

		if self.model() == model:
			return
		
		elif not isinstance(model, viewmodels.BSBinViewProxyModel):
			raise TypeError(f"Model must be a BSBinViewProxyModel (got {type(model)})")
		
		# TODO: Disconnect old model...?
		
		model.columnsInserted.connect(self.setColumnWidthsFromBinView)

		super().setModel(model)

	@QtCore.Slot(object)
	def selectSectionFromCoordinates(self, viewport_coords:QtCore.QPoint):

		section_logical = self.header().logicalIndexAt(viewport_coords.x())
		self.selectSection(section_logical)

	@QtCore.Slot(int)
	def selectSection(self, column_logical:int):

		self.toggleSelectionBehavior(
			QtWidgets.QTreeView.SelectionBehavior.SelectColumns,
			keep_current_selection = QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
		)

		if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
			selection_behavior_flags = QtCore.QItemSelectionModel.SelectionFlag.Toggle

		else:
			selection_behavior_flags = QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect

		self.selectionModel().select(
			QtCore.QItemSelection(self.model().index(0, column_logical), self.model().index(self.model().rowCount()-1, column_logical)),
			QtCore.QItemSelectionModel.SelectionFlag.Columns|
			selection_behavior_flags
		)

	def copySelection(self):
		"""Copy selection to clipboard"""
     
		# TODO: Messssssy
		# TODO: This'll be good to refactor for ALE/CSV/JSON exports, yay!

		if not self.selectionModel().hasSelection():

			logging.getLogger(__name__).debug("Nothing selected to copy")
			return

		# Figure out which columns are selected, total
		selected_columns_visual = sorted(
			set(self.header().visualIndex(i.column()) for i in self.selectedIndexes())
		)


		# Collect header strings from selected columns
		headers_text:dict[int,str] = dict()

		for col_vis in selected_columns_visual:

			col_logical = self.header().logicalIndex(col_vis)

			header_text = self.model().headerData(
				col_logical,
				QtCore.Qt.Orientation.Horizontal,
				QtCore.Qt.ItemDataRole.DisplayRole,
			)

			# NOTE: Needed?
			headers_text[col_vis] = header_text if isinstance(header_text,str) else ""

		# Collect item strings from selected bin items
		rows_text:list[dict[int, str]] = []

		last_row = None

		for item_index in sorted(self.selectedIndexes(), key=lambda i: i.row()):

			if item_index.row() != last_row:
				last_row = item_index.row()
				rows_text.append(dict())

			item_text   = item_index.data(
				QtCore.Qt.ItemDataRole.DisplayRole,
			)

			rows_text[-1][self.header().visualIndex(item_index.column())] = item_text if isinstance(item_text, str) else ""



		# Join all together

		final_headers = "\t".join(headers_text[c] for c in selected_columns_visual)
		final_items   = "\n".join(
			"\t".join(i.get(c,"") for c in selected_columns_visual) for i in rows_text
		)

		QtWidgets.QApplication.clipboard().setText("\n".join([final_headers, final_items]))

	def toggleSelectionBehavior(self, behavior:QtWidgets.QTreeView.SelectionBehavior|None=None, keep_current_selection:bool=False):

		behavior = behavior or BSTextViewModeConfig.DEFAULT_SELECTION_BEHAVIOR

		if self.selectionBehavior() == behavior:

			#logging.getLogger(__name__).debug("Selection behavior already %s. Not changed.", behavior)
			return

		# NOTE: BIG NOTE: TODO: ETC:
		# Disabling keep_current_selection for all instances for now
		keep_current_selection = keep_current_selection and BSTextViewModeConfig.ALLOW_KEEP_CURRENT_SELECTION_BETWEEN_MODES

		if not keep_current_selection:
			self.clearSelection()

		self.setSelectionBehavior(behavior)

		if behavior == QtWidgets.QTreeView.SelectionBehavior.SelectItems:
			self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.MultiSelection)

		else:
			self.setSelectionMode(BSTextViewModeConfig.DEFAULT_SELECTION_MODE)

		logging.getLogger(__name__).debug("Treeview selection changed to behavior=%s, mode=%s", self.selectionBehavior(), self.selectionMode())


	def keyPressEvent(self, event):

		if event.matches(QtGui.QKeySequence.StandardKey.Copy) and not event.isAutoRepeat():

			self.copySelection()
			event.accept()

		else:
			return super().keyPressEvent(event)


	def mousePressEvent(self, event:QtGui.QMouseEvent):

		if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
			self.toggleSelectionBehavior(QtWidgets.QTreeView.SelectionBehavior.SelectItems, keep_current_selection=(event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier))
			#event.accept()
		else:
			self.toggleSelectionBehavior()
			#event.accept()

		return super().mousePressEvent(event)


	@QtCore.Slot(object, int)
	@QtCore.Slot(object, int, int)
	@QtCore.Slot(object, int, int, bool)
	def setColumnWidthsFromBinView(self, parent_index:QtCore.QModelIndex, source_start:int, source_end:int|None=None, autosize_if_undefined:bool=True):

		if parent_index.isValid():
			return

		if source_end is None:
			source_end = source_start

		for col_index_logical in range(source_start, source_end+1):

			self.setColumnWidthFromBinView(
				col_index_logical,
				autosize_if_undefined
			)

	@QtCore.Slot(int)
	@QtCore.Slot(int, bool)
	def setColumnWidthFromBinView(self, col_index_logical:int, autosize_if_undefined:bool=True):
		"""Set column width from stored bin view, or resize to contents"""

		column_width = self.model().headerData(
			col_index_logical,
			QtCore.Qt.Orientation.Horizontal,
			viewmodels.viewmodelitems.BSBinColumnDataRoles.BSColumnWidth # Column width, if specified by bin view
		)

		if column_width:
			self.setColumnWidth(col_index_logical, column_width + self._item_padding.left() + self._item_padding.right())

		elif autosize_if_undefined:
			self.resizeColumnToContents(col_index_logical)

	@QtCore.Slot(QtCore.QMarginsF)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		"""Set item padding and add frame size padding"""

		if self._item_padding == padding:
			return
		
		self._item_padding = QtCore.QMarginsF(padding)

		for delegate in self._delegate_provider.delegates():
			delegate.setItemPadding(padding)

		logging.getLogger(__name__).debug("Setting padding to %s", str(self._item_padding))
		
		self.scheduleDelayedItemsLayout()

		#self.update()
		self.sig_item_padding_changed.emit(padding)

	@QtCore.Slot(object)
	def setDefaultSortColumns(self, sort_columns:list[list[int,str]]):

		self._default_sort = sort_columns
		self.sig_default_sort_columns_changed.emit(self._default_sort)

	def registerCustomDelegates(self):
		"""Register custom delegates, but probably not here"""

		# Clip Color
		self._delegate_provider.setUniqueDelegateForField(
			51, itemdelegates.BSIconLookupItemDelegate(
				parent=self,
				aspect_ratio=self.ICON_ASPECT_RATIO,
				icon_provider=icon_providers.BSStyledClipColorIconProvider(),
			)
		)


		# Markers
		self._delegate_provider.setUniqueDelegateForField(
			132,
			itemdelegates.BSIconLookupItemDelegate(
				parent=self,
				aspect_ratio=self.ICON_ASPECT_RATIO,
				icon_provider=icon_providers.BSStyledMarkerIconProvider(),
			)
		)

		# Bin Display Item Icon
		self._delegate_provider.setUniqueDelegateForField(
			200,
			itemdelegates.BSIconLookupItemDelegate(
				parent=self,
				aspect_ratio=self.ICON_ASPECT_RATIO,
				icon_provider=icon_providers.BSStyledBinItemTypeIconProvider(path_registry=self._bin_item_icon_registry),
			)

		)