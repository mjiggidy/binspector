"""
Bin settings views, typically used as toolboxes or sidebars
"""

from PySide6 import QtCore, QtGui, QtWidgets
from ..views import treeview, enumview
import avbutils

class BSBinAppearanceSettingsView(QtWidgets.QWidget):
	"""Fonts, colors, and dimensions"""

	sig_font_changed = QtCore.Signal(QtGui.QFont)
	sig_palette_changed = QtCore.Signal(QtGui.QPalette)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._spn_geo_x = QtWidgets.QSpinBox()
		self._spn_geo_x.setSuffix(" px")
		self._spn_geo_x.setMaximum(9999)
		self._spn_geo_x.setMinimum(-9999)
		self._spn_geo_x.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		self._spn_geo_y = QtWidgets.QSpinBox()
		self._spn_geo_y.setSuffix(" px")
		self._spn_geo_y.setMaximum(9999)
		self._spn_geo_y.setMinimum(-9999)
		self._spn_geo_y.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

		self._spn_geo_w = QtWidgets.QSpinBox()
		self._spn_geo_w.setSuffix(" px")
		self._spn_geo_w.setMaximum(9999)
		self._spn_geo_w.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		#self._spn_geo_w.setMinimum(-9999)
		self._spn_geo_h = QtWidgets.QSpinBox()
		self._spn_geo_h.setSuffix(" px")
		self._spn_geo_h.setMaximum(9999)
		self._spn_geo_h.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		#self._spn_geo_h.setMinimum(-9999)

		self.layout().addWidget(QtWidgets.QLabel("Window Geometry"))
		
		lay_geo= QtWidgets.QGridLayout()
		lay_geo.addWidget(QtWidgets.QLabel("X:"), 0, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_x, 0, 1)
		lay_geo.addWidget(QtWidgets.QLabel("Y:"), 1, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_y, 1, 1)
		
		lay_geo.setColumnStretch(2, 1)
		
		lay_geo.addWidget(QtWidgets.QLabel("W:"), 0, 3, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_w, 0, 4)
		lay_geo.addWidget(QtWidgets.QLabel("H:"), 1, 3, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_h, 1, 4)
		#lay_geo_dimensions.addStretch()

		self.layout().addLayout(lay_geo)

		self._chk_was_iconic = QtWidgets.QCheckBox("Was Iconic")
		self.layout().addWidget(self._chk_was_iconic)

		lay_fonts = QtWidgets.QHBoxLayout()
		self._cmb_fonts = QtWidgets.QFontComboBox()
		self._spn_size  = QtWidgets.QSpinBox(minimum=8, maximum=100)	# Avid font dialog extents

		self.layout().addWidget(QtWidgets.QLabel("Font And Colors"))
		lay_fonts.addWidget(self._cmb_fonts)
		lay_fonts.addWidget(self._spn_size)

		self.layout().addLayout(lay_fonts)

		lay_colors = QtWidgets.QHBoxLayout()
		self._btn_fg_color = QtWidgets.QPushButton()
		self._btn_bg_color = QtWidgets.QPushButton()

		lay_colors.addWidget(self._btn_fg_color)
		lay_colors.addWidget(self._btn_bg_color)

		self.layout().addLayout(lay_colors)

		self._tree_column_widths = treeview.LBTreeView()
		self.layout().addWidget(QtWidgets.QLabel("Column Widths"))
		self.layout().addWidget(self._tree_column_widths)

		

		self._cmb_fonts.currentFontChanged.connect(self.sig_font_changed)
		self._spn_size.valueChanged.connect(lambda: self.sig_font_changed.emit(self.binFont()))

		self._btn_fg_color.clicked.connect(self.fgColorPickerRequested)
		self._btn_bg_color.clicked.connect(self.bgColorPickerRequested)

	@QtCore.Slot(bool)
	def setWasIconic(self, was_iconic:bool):
		#print(was_iconic)
		self._chk_was_iconic.setChecked(was_iconic)

	# TODO I'm sure this can be one method
	@QtCore.Slot()
	def bgColorPickerRequested(self):
		
		bg_color,_ = self.binPalette()
		new_color = QtWidgets.QColorDialog.getColor(bg_color, self._btn_fg_color, "Choose a text color")
		
		if new_color.isValid():
			self.setBinBackgroundColor(new_color)

	@QtCore.Slot()
	def fgColorPickerRequested(self):
		
		fg_color,_ = self.binPalette()
		new_color = QtWidgets.QColorDialog.getColor(fg_color, self._btn_fg_color, "Choose a text color")

		if new_color.isValid():
			self.setBinForegroundColor(new_color)
	
	@QtCore.Slot(QtCore.QRect)
	def setBinRect(self, rect:QtCore.QRect):
		#print(rect)
		
		self._spn_geo_x.setValue(rect.x())
		self._spn_geo_y.setValue(rect.y())
		self._spn_geo_w.setValue(rect.width())
		self._spn_geo_h.setValue(rect.height())

	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, font:QtGui.QFont):

		self._cmb_fonts.setCurrentFont(font)
		self._spn_size.setValue(font.pixelSize())

	@QtCore.Slot(QtGui.QColor)
	def setBinForegroundColor(self, color:QtGui.QColor):
		
		fg = self._btn_fg_color.palette()
		fg.setColor(QtGui.QPalette.ColorRole.Button, color)
		
		self._btn_fg_color.setPalette(fg)
		self._btn_fg_color.setText(self._format_color_text(fg.color(QtGui.QPalette.ColorRole.Button)))
		self.sig_palette_changed.emit(self.binPalette())

	@QtCore.Slot(QtGui.QColor)
	def setBinBackgroundColor(self, color:QtGui.QColor):
		
		bg = self._btn_bg_color.palette()
		bg.setColor(QtGui.QPalette.ColorRole.Button, color)
		
		self._btn_bg_color.setPalette(bg)
		self._btn_bg_color.setText(self._format_color_text(bg.color(QtGui.QPalette.ColorRole.Button)))

		self.sig_palette_changed.emit(self.binPalette())
	
	@staticmethod
	def _format_color_text(color:QtGui.QColor) -> str:
		return f"R: {color.red()}  G: {color.green()}  B: {color.blue()}"

	@QtCore.Slot(QtGui.QPalette)
	def setBinPalette(self, fg_color:QtGui.QColor, bg_color:QtGui.QColor):

		self.blockSignals(True)
		self.setBinForegroundColor(fg_color)
		self.setBinBackgroundColor(bg_color)
		self.blockSignals(False)
		self.sig_palette_changed.emit(self.binPalette())
	
	def binFont(self) -> QtGui.QFont:
		font = self._cmb_fonts.currentFont()
		font.setPixelSize(self._spn_size.value())
		return font
	
	def binPalette(self) -> tuple[QtGui.QColor, QtGui.QColor]:
		"""Returns a tuple of `(fg_color:QtGui.QColor, bg_color:QtGui.QColor)`.  Weird notation lol"""

		return (
			self._btn_fg_color.palette().color(QtGui.QPalette.ColorRole.Button),
			self._btn_bg_color.palette().color(QtGui.QPalette.ColorRole.Button),
		)
	
class BSBinDisplaySettingsView(enumview.LBAbstractEnumFlagsView):
	"""Flags for setting Bin Item Display filter"""

	def __init__(self, bin_items_flags:avbutils.BinDisplayItemTypes|None=None, *args, **kwargs):
		
		super().__init__(bin_items_flags if bin_items_flags is not None else avbutils.BinDisplayItemTypes(0), *args, **kwargs)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(3,0,3,0)

		grp_clips = QtWidgets.QGroupBox(title="Clip Types")

		grp_clips.setLayout(QtWidgets.QVBoxLayout())
		grp_clips.layout().setSpacing(0)
		grp_clips.layout().setContentsMargins(3,0,3,0)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.MASTER_CLIP]
		chk.setText("Master Clips")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.LINKED_MASTER_CLIP]
		chk.setText("Linked Master Clips")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SUBCLIP]
		chk.setText("Subclips")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SEQUENCE]
		chk.setText("Sequences")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SOURCE]
		chk.setText("Sources")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.EFFECT]
		chk.setText("Effects")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.MOTION_EFFECT]
		chk.setText("Motion Effects")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.PRECOMP_RENDERED_EFFECT]
		chk.setText("Precompute Clips - Rendered Effects")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.PRECOMP_TITLE_MATTEKEY]
		chk.setText("Precompute Clips - Titles and Matte Keys")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.GROUP]
		chk.setText("Groups")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.STEREOSCOPIC_CLIP]
		chk.setText("Stereoscopic Clips")
		grp_clips.layout().addWidget(chk)

		self.layout().addWidget(grp_clips)

		grp_origins = QtWidgets.QGroupBox(title="Clip Origins")
		grp_origins.setLayout(QtWidgets.QVBoxLayout())
		grp_origins.layout().setSpacing(0)
		grp_origins.layout().setContentsMargins(3,0,3,0)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.USER_CLIP]
		chk.setText("Show clips created by user")
		grp_origins.layout().addWidget(chk)
		
		chk = self._option_mappings[avbutils.BinDisplayItemTypes.REFERENCE_CLIP]
		chk.setText("Show reference clips")
		grp_origins.layout().addWidget(chk)
		

		self.layout().addWidget(grp_origins)

		self.layout().addStretch()

class BSBinSiftSettingsView(QtWidgets.QWidget):
	"""Bin Sift Settings"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setContentsMargins(0,0,0,0)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)

		self._chk_sift_enabled = QtWidgets.QCheckBox("Sift Enabled")

		self._tree_siftsettings = treeview.LBTreeView()

		self.layout().addWidget(self._chk_sift_enabled)
		self.layout().addWidget(self._tree_siftsettings)