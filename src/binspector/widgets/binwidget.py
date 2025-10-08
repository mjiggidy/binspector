from PySide6 import QtCore, QtGui, QtWidgets
import avbutils
from ..views import bintreeview

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_request_open_bin = QtCore.Signal()
	sig_request_bin_display  = QtCore.Signal()
	sig_request_display_mode = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		#self.setContentsMargins(0,0,0,0)
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)

		self._section_top       = QtWidgets.QToolBar()
		self._tree_bin_contents = bintreeview.LBBinTreeView()
		self._section_bottom    = QtWidgets.QWidget()

		self.layout().addWidget(self._section_top)
		self.layout().addWidget(self._tree_bin_contents)
		self.layout().addWidget(self._section_bottom)

		#self._section_top.setLayout(QtWidgets.QHBoxLayout())
		#self._section_top.layout().setContentsMargins(0,0,0,0)
		#self._section_top.layout().setSpacing(0)

		toolbar_font = self._section_top.font()
		toolbar_font.setPointSizeF(toolbar_font.pointSizeF() * 0.8)
		self._section_top.setFont(toolbar_font)
		self._section_bottom.setFont(toolbar_font)

		#self._cmb_bin_view_list = QtWidgets.QComboBox()
		#self._cmb_bin_view_list.setSizePolicy(self._cmb_bin_view_list.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.MinimumExpanding)
#
		#self._btngrp_view_modes = QtWidgets.QButtonGroup()
		#self._btngrp_view_modes.idClicked.connect(lambda id: self.sig_request_display_mode.emit(avbutils.BinDisplayModes(id)))
		#self.sig_request_display_mode.connect(lambda d: print(d.name))
#
		#self._btn_view_list = QtWidgets.QPushButton()
		#self._btn_view_list.setCheckable(True)
		#self._btn_view_list.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FormatTextDirectionLtr))
#
		#self._btn_view_script = QtWidgets.QPushButton()
		#self._btn_view_script.setCheckable(True)
		#self._btn_view_script.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentProperties))
#
		#self._btn_view_frame = QtWidgets.QPushButton()
		#self._btn_view_frame.setCheckable(True)
		#self._btn_view_frame.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.CameraPhoto))
#
		#self._btngrp_view_modes.addButton(self._btn_view_list)
		#self._btngrp_view_modes.setId(self._btn_view_list, avbutils.BinDisplayModes.LIST.value)
		#self._btngrp_view_modes.addButton(self._btn_view_script)
		#self._btngrp_view_modes.setId(self._btn_view_script, avbutils.BinDisplayModes.SCRIPT.value)
		#self._btngrp_view_modes.addButton(self._btn_view_frame)
		#self._btngrp_view_modes.setId(self._btn_view_frame, avbutils.BinDisplayModes.FRAME.value)
#
		#self._btn_request_open = QtWidgets.QPushButton("&Open Bin...")
		#self._btn_request_open.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentOpen))
		#self._btn_request_open.clicked.connect(self.sig_request_open_bin)
		#
		#self._section_top.addWidget(self._btn_request_open)
		
		sep = QtWidgets.QWidget()
		sep.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		#self._section_top.addWidget(sep)
		#self._section_top.addWidget(self._cmb_bin_view_list)
		#self._section_top.addWidget(self._btn_view_list)
		#self._section_top.addWidget(self._btn_view_script)
		#self._section_top.addWidget(self._btn_view_frame)

		self._section_bottom.setLayout(QtWidgets.QHBoxLayout())
		self._section_bottom.layout().setContentsMargins(2,2,2,2)

		self._section_bottom.layout().addStretch()
		self._lbl_bin_item_count = QtWidgets.QLabel()
		self._section_bottom.layout().addWidget(self._lbl_bin_item_count)

		self._btn_show_bin_display = QtWidgets.QPushButton()
		self._btn_show_bin_display.setCheckable(True)
		self._btn_show_bin_display.toggled.connect(self.sig_request_bin_display)
		self._btn_show_bin_display.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.GoNext))

		self._section_bottom.layout().addWidget(self._btn_show_bin_display)


	def treeView(self) -> bintreeview.LBBinTreeView:
		"""Get the main view"""
		return self._tree_bin_contents
	
	def setTreeView(self, treeview:bintreeview.LBBinTreeView):
		self._tree_bin_contents = treeview
	
	def topSectionWidget(self) -> QtWidgets.QWidget:
		return self._section_top
	
	def setTopSectionWidget(self, widget:QtWidgets.QWidget):
		self._section_top = widget
	
	def bottomSectionWidget(self) -> QtWidgets.QWidget:
		return self._section_bottom
	
	def setBottomSectionWidget(self, widget:QtWidgets.QWidget):
		self._section_bottom = widget
	
	@QtCore.Slot(object)
	def setDisplayMode(self, mode:avbutils.BinDisplayModes):
		pass
		#self._btngrp_view_modes.button(mode.value).setChecked(True)

	@QtCore.Slot()
	def _connectSourceModelSlots(self):

		source_model = self._tree_bin_contents.model().sourceModel()

		if not source_model:
			return
		
		source_model.rowsInserted.connect(self.updateBinStats)
		source_model.rowsRemoved.connect(self.updateBinStats)
		source_model.modelReset.connect(self.updateBinStats)

	@QtCore.Slot()
	def updateBinStats(self):

		#print("HI")

		count_visible = self._tree_bin_contents.model().rowCount()
		count_all = self._tree_bin_contents.model().sourceModel().rowCount()
		self._lbl_bin_item_count.setText(f"Showing {QtCore.QLocale.system().toString(count_visible)} of {QtCore.QLocale.system().toString(count_all)} items")
	