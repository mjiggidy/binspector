import logging
from PySide6 import QtCore, QtGui, QtWidgets

from ..core.config import BSTextViewModeConfig
from ..models import viewmodels
from ..views  import treeview
from ..utils import columnselect
from ..res import icons_binitems
from ..binwidget import delegate_lookup

class BSBinTextView(treeview.BSTreeViewBase):
	"""QTreeView but nicer"""

	sig_default_sort_columns_changed = QtCore.Signal(object)
	"""TODO: HMMMMMM"""

	sig_selection_model_changed      = QtCore.Signal(object)
	"""Selection model was changed"""

	sig_item_padding_changed         = QtCore.Signal(object)


	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setModel(viewmodels.BSBinViewProxyModel())
		self.setSelectionBehavior(BSTextViewModeConfig.DEFAULT_SELECTION_BEHAVIOR)
		self.setSelectionMode(BSTextViewModeConfig.DEFAULT_SELECTION_MODE)

		self._delegate_provider     = delegate_lookup.BSBinColumnDelegateProvider(view=self)
		self._column_select_watcher = columnselect.BSColumnSelectWatcher(parent=self)
		self._item_padding          = QtCore.QMarginsF(BSTextViewModeConfig.DEFAULT_ITEM_PADDING)

		#self.setItemPadding(self._item_padding)
		
		self.header().viewport().installEventFilter(self._column_select_watcher)

		self.header().sectionCountChanged.connect(lambda: self.refreshDelegates())
		self._column_select_watcher.sig_column_selected.connect(self.selectSectionFromCoordinates)

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
		
		#self.setCustomDelegates()

	def delegateProvider(self) -> delegate_lookup.BSBinColumnDelegateProvider:
		"""Get the thing that looks up delegates for the thing"""

		return self._delegate_provider

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

#	def setCustomDelegates(self):
#		"""Temp"""
#
#		# Clip color chips
#		clip_color_delegate = delegate_lookup.ITEM_DELEGATES_PER_FIELD_ID[51]
#		clip_color_delegate.iconProvider().addIcon(-1, QtGui.QIcon(icon_engines.BSPalettedClipColorIconEngine(clip_color=QtGui.QColor())))
#		for color in avbutils.get_default_clip_colors():
#
#			icon_color = QtGui.QColor.fromRgba64(*color.as_rgba16())
#			icon = QtGui.QIcon(icon_engines.BSPalettedClipColorIconEngine(clip_color=icon_color))
#			clip_color_delegate.iconProvider().addIcon(icon_color.toTuple(), icon)
#
#		# Marker icons
#		marker_delegate = delegate_lookup.ITEM_DELEGATES_PER_FIELD_ID[132]
#		marker_delegate.iconProvider().addIcon(-1, QtGui.QIcon(icon_engines.BSPalettedMarkerIconEngine(marker_color=QtGui.QColor())))
#		for marker_color in avbutils.MarkerColors:
#
#			marker_color = QtGui.QColor(marker_color.value)
#			icon = QtGui.QIcon(icon_engines.BSPalettedMarkerIconEngine(marker_color=marker_color))
#			marker_delegate.iconProvider().addIcon(marker_color.toTuple(), icon)
#
#		# Bin item type icons
#		# TODO/TEMP: Prep bin display item type icons
#		item_type_delegate = delegate_lookup.ITEM_DELEGATES_PER_FIELD_ID[200]
#		for item_type in avbutils.bins.BinDisplayItemTypes:
#			item_type_delegate.iconProvider().addIcon(
#				item_type|avbutils.bins.BinDisplayItemTypes.USER_CLIP,
#				QtGui.QIcon(
#					icon_engines.BSPalettedSvgIconEngine(
#					":/icons/binitems/item_masterclip.svg",
#					)
#				)
#			)


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

#		print("*** Received", padding)

		if self._item_padding == padding:
			return
		
		self._item_padding = QtCore.QMarginsF(padding)
#		print("*** ITEM PADDING NOW ", self._item_padding)
		self.refreshDelegates()

		logging.getLogger(__name__).debug("Setting padding to %s", str(self._item_padding))

		self.sig_item_padding_changed.emit(padding)

	def refreshDelegates(self, adjusted_padding:QtCore.QMarginsF|None=None):
		"""Re-calculate and re-apply padding data when size stuff changes"""

		adjusted_padding = QtCore.QMarginsF(adjusted_padding if adjusted_padding is not None else self._item_padding)
#		print("****OKAY STARTING WITH", adjusted_padding)
		
		done_dels = set()

		# Set padding on default del
		current_del = self._delegate_provider.defaultItemDelegate()
		current_del.setItemPadding(adjusted_padding)
		
		self._delegate_provider.setDefaultItemDelegate(current_del)

		done_dels.add(current_del)

		# Set padding on any other delegates
		for col in range(self.header().count()):
		
			current_del = self._delegate_provider.delegateForColumn(col)

			if current_del not in done_dels:
				current_del.setItemPadding(adjusted_padding)
				done_dels.add(current_del)

			self._delegate_provider.setDelegateForColumn(col, current_del)
			
#		for test_Del in done_dels:
#			print(test_Del.itemPadding())


	def sizeHintForColumn(self, column) -> int:
		"""Column width"""

		return super().sizeHintForColumn(column)

	@QtCore.Slot(object)
	def setDefaultSortColumns(self, sort_columns:list[list[int,str]]):

		self._default_sort = sort_columns
		self.sig_default_sort_columns_changed.emit(self._default_sort)