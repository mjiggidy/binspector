import logging
from PySide6 import QtWidgets, QtCore, QtGui
import avbutils
from . import treeview
from .delegates import binitems
from ..models import viewmodels
from ..views.delegates import binitems
from ..core import icons
from ..res import icons_binitems

class BSColumnSelectWatcher(QtCore.QObject):

	DEFAULT_SELECTION_MODIFIER = QtGui.Qt.KeyboardModifier.AltModifier

	sig_column_selection_activated = QtCore.Signal(bool)
	sig_column_selected            = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		# Start out accurate!
		self._column_selection_active = bool(QtWidgets.QApplication.keyboardModifiers() & self.DEFAULT_SELECTION_MODIFIER)

	def columnSelectionIsActive(self) -> bool:
		"""Column selection mode currently active"""

		return self._column_selection_active
	
	def setColumnSelectionActive(self, is_active:bool):
		"""Indicate column selection has begun"""

		if is_active != self._column_selection_active:

			self._column_selection_active = is_active
			
			logging.getLogger(__name__).debug("Column selection changed to %s", self.columnSelectionIsActive())
			self.sig_column_selection_activated.emit(is_active)

	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:

		if event.type() == QtCore.QEvent.Type.MouseButtonPress:
			
			if not event.button() & QtCore.Qt.MouseButton.LeftButton:
				return super().eventFilter(watched, event)
	
			# If clicked with modifier key: Column select begin!
			if not event.modifiers() & self.DEFAULT_SELECTION_MODIFIER:
				return super().eventFilter(watched, event)
			
			self.setColumnSelectionActive(True)
				
			
			if self.columnSelectionIsActive():
				event = QtGui.QMouseEvent(event)
				self.sig_column_selected.emit(event.localPos())
			
			return True

		if event.type() == QtCore.QEvent.Type.MouseButtonRelease and self.columnSelectionIsActive():
			
			# On mouse release, we done wit dat column selection
			self.setColumnSelectionActive(False)
			return True

		return super().eventFilter(watched, event)

class BSBinTreeView(treeview.LBTreeView):
	"""QTreeView but nicer"""

	sig_default_sort_columns_changed = QtCore.Signal(object)
	"""TODO: HMMMMMM"""

	sig_selection_model_changed = QtCore.Signal(object)
	"""Selection model was changed"""

	DEFAULT_ITEM_PADDING:QtCore.QMargins = QtCore.QMargins(16,4,16,4)
	"""Default padding inside view item"""

	SELECTION_BEHAVIOR_KEY     = QtCore.Qt.Key.Key_Alt
	DEFAULT_SELECTION_BEHAVIOR = QtWidgets.QTreeView.SelectionBehavior.SelectRows
	DEFAULT_SELECTION_MODE     = QtWidgets.QTreeView.SelectionMode    .ExtendedSelection
	
	ALLOW_KEEP_CURRENT_SELECTION_BETWEEN_MODES = False
	"""Actually allow `keep_current_selection` bool argument to take effect"""

	BINVIEW_COLUMN_WIDTH_ADJUST:int = 64
	"""Adjust binview-specified column widths for better fit"""

	ITEM_DELEGATES_PER_FIELD_ID = {
		51 : binitems.BSIconLookupItemDelegate(aspect_ratio=QtCore.QSize(4,3), padding=DEFAULT_ITEM_PADDING), # Clip color
		132: binitems.BSIconLookupItemDelegate(aspect_ratio=QtCore.QSize(4,3), padding=DEFAULT_ITEM_PADDING), # Marker
		200: binitems.BSIconLookupItemDelegate(aspect_ratio=QtCore.QSize(4,3), padding=DEFAULT_ITEM_PADDING), # Bin Display Item Type

	}
	"""Specialized one-off fields"""

	ITEM_DELEGATES_PER_FORMAT_ID = {
		avbutils.BinColumnFormat.TIMECODE: binitems.LBTimecodeItemDelegate(padding=DEFAULT_ITEM_PADDING),
	}
	"""Delegate for generic field formats"""

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)		

		self._palette_watcher = icons.BSPaletteWatcherForSomeReason()
		self._column_select_watcher = BSColumnSelectWatcher()
		
		self.setModel((viewmodels.LBSortFilterProxyModel()))

		self.setSelectionBehavior(self.DEFAULT_SELECTION_BEHAVIOR)
		self.setSelectionMode(self.DEFAULT_SELECTION_MODE)

		# TODO/TEMP: Prep clip color icons

		self.header().viewport().installEventFilter(self._column_select_watcher)
		self._column_select_watcher.sig_column_selected.connect(self.selectSectionFromCoordinates)

	def setSelectionModel(self, selectionModel):
		
		if selectionModel != self.selectionModel():
		
			logging.getLogger(__name__).error("BinTreeView changed selection model to %s", selectionModel)
			self.sig_selection_model_changed.emit(selectionModel)

			return super().setSelectionModel(selectionModel)

	def setModel(self, model):

		super().setModel(model)

		self.model().columnsInserted.connect(self.setColumnWidthsFromBinView)
		self.model().columnsInserted.connect(
			lambda parent_index, source_start, source_end:
			self.assignItemDelegates(parent_index, source_start)
		)
		self.model().columnsMoved.connect(
			lambda source_parent,
				source_logical_start,
				source_logical_end, 
				destination_parent,
				destination_logical_start:	# NOTE: Won't work for heirarchical models
			self.assignItemDelegates(destination_parent, min(source_logical_start, destination_logical_start))
		)

		self.setItemDelegate(binitems.BSGenericItemDelegate(padding=self.DEFAULT_ITEM_PADDING))
		self.setCustomDelegates()
	
	@QtCore.Slot(object)
	def selectSectionFromCoordinates(self, viewport_coords:QtCore.QPoint):
		
		section_logical = self.header().logicalIndexAt(viewport_coords.x())
		self.selectSection(section_logical)
		#print(self.model().headerData(section_logical, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole))

	@QtCore.Slot(int)
	def selectSection(self, column_logical:int):

		# TODO: TESTING WIHTOUT
		#if not QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
		#	logging.getLogger(__name__).debug("NAAAH")
		#	return
		
		
		
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

		behavior = behavior or self.DEFAULT_SELECTION_BEHAVIOR

		if self.selectionBehavior() == behavior:
			
			logging.getLogger(__name__).debug("Selection behavior already %s. Not changed.", behavior)
			return
		
		# NOTE: BIG NOTE: TODO: ETC:
		# Disabling keep_current_selection for all instances for now
		keep_current_selection = keep_current_selection and self.ALLOW_KEEP_CURRENT_SELECTION_BETWEEN_MODES
		
		if not keep_current_selection:
			self.clearSelection()

		self.setSelectionBehavior(behavior)
		
		if behavior == QtWidgets.QTreeView.SelectionBehavior.SelectItems:
			self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.MultiSelection)

		else:
			self.setSelectionMode(self.DEFAULT_SELECTION_MODE)
		
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

	def setCustomDelegates(self):
		"""Temp"""

		# Clip color chips
		clip_color_delegate = self.ITEM_DELEGATES_PER_FIELD_ID[51]
		clip_color_delegate.iconProvider().addIcon(-1, QtGui.QIcon(icons.BSPalettedClipColorIconEngine(clip_color=QtGui.QColor(), palette_watcher=self._palette_watcher)))
		for color in avbutils.get_default_clip_colors():

			icon_color = QtGui.QColor.fromRgba64(*color.as_rgba16())
			icon = QtGui.QIcon(icons.BSPalettedClipColorIconEngine(clip_color=icon_color, palette_watcher=self._palette_watcher))
			clip_color_delegate.iconProvider().addIcon(icon_color.toTuple(), icon)

		# Marker icons
		marker_delegate = self.ITEM_DELEGATES_PER_FIELD_ID[132]
		marker_delegate.iconProvider().addIcon(-1, QtGui.QIcon(icons.BSPalettedMarkerIconEngine(marker_color=QtGui.QColor(), palette_watcher=self._palette_watcher)))
		for marker_color in avbutils.MarkerColors:

			marker_color = QtGui.QColor(marker_color.value)
			icon = QtGui.QIcon(icons.BSPalettedMarkerIconEngine(marker_color=marker_color, palette_watcher=self._palette_watcher))
			marker_delegate.iconProvider().addIcon(marker_color.toTuple(), icon)

		# Bin item type icons
		# TODO/TEMP: Prep bin display item type icons
		item_type_delegate = self.ITEM_DELEGATES_PER_FIELD_ID[200]
		for item_type in avbutils.bins.BinDisplayItemTypes:
			item_type_delegate.iconProvider().addIcon(
				item_type|avbutils.bins.BinDisplayItemTypes.USER_CLIP,
				QtGui.QIcon(
					icons.BSPalettedSvgIconEngine(
					":/icons/binitems/item_masterclip.svg",
					palette_watcher=self._palette_watcher
					)
				)
			)

	@QtCore.Slot(object, int, int)
	def assignItemDelegates(self, parent_index:QtCore.QModelIndex, logical_start_column:int):
		"""Assign item delegates starting with the first changed logical row, cascaded through to the end"""

		if parent_index.isValid():
			return
		
		for col in range(logical_start_column, self.model().columnCount()):
			
			field_id     = self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+1)
			format_id    = self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole+2)

			item_delegate = self.itemDelegate()


			# Look up specialized fields
			if field_id in self.ITEM_DELEGATES_PER_FIELD_ID:
				item_delegate = self.ITEM_DELEGATES_PER_FIELD_ID[field_id]
			# Look up specialized generic formats
			elif format_id in self.ITEM_DELEGATES_PER_FORMAT_ID:
				item_delegate = self.ITEM_DELEGATES_PER_FORMAT_ID[format_id]
			
			self.setItemDelegateForColumn(col, item_delegate)
	
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
			QtCore.Qt.ItemDataRole.UserRole+4	# Column width, if specified by bin view
		)
		
		if column_width:
			self.setColumnWidth(col_index_logical, column_width + self.DEFAULT_ITEM_PADDING.left() + self.DEFAULT_ITEM_PADDING.right())
		
		elif autosize_if_undefined:
			self.resizeColumnToContents(col_index_logical)

	def sizeHintForColumn(self, column) -> int:
		"""Column width"""

		return super().sizeHintForColumn(column)
	
	@QtCore.Slot(object)
	def setDefaultSortColumns(self, sort_columns:list[list[int,str]]):

		self._default_sort = sort_columns
		self.sig_default_sort_columns_changed.emit(self._default_sort)
	
	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMargins):

		self.itemDelegate().setItemPadding(padding)
		for delegate in self.ITEM_DELEGATES_PER_FIELD_ID.values():
			#print("Here")
			delegate.setItemPadding(padding)