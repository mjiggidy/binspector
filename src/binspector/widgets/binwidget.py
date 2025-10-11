from PySide6 import QtCore, QtGui, QtWidgets
import avbutils
from ..views import bintreeview

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())

		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)

		self._section_top       = QtWidgets.QToolBar()
		self._tree_bin_contents = bintreeview.BSBinTreeView()
		self._section_bottom    = QtWidgets.QToolBar()

		self.layout().addWidget(self._section_top)
		self.layout().addWidget(self._tree_bin_contents)
		self.layout().addWidget(self._section_bottom)

		toolbar_font = self._section_top.font()
		toolbar_font.setPointSizeF(toolbar_font.pointSizeF() * 0.8)
		self._section_top.setFont(toolbar_font)
		self._section_bottom.setFont(toolbar_font)


	def treeView(self) -> bintreeview.BSBinTreeView:
		"""Get the main view"""
		return self._tree_bin_contents
	
	def setTreeView(self, treeview:bintreeview.BSBinTreeView):
		self._tree_bin_contents = treeview
	
	def topSectionWidget(self) -> QtWidgets.QToolBar:
		return self._section_top
	
	def setTopSectionWidget(self, toolbar:QtWidgets.QToolBar):
		self._section_top = toolbar
	
	def bottomSectionWidget(self) -> QtWidgets.QWidget:
		return self._section_bottom
	
	def setBottomSectionWidget(self, widget:QtWidgets.QWidget):
		self._section_bottom = widget
	
	@QtCore.Slot(object)
	def setDisplayMode(self, mode:avbutils.BinDisplayModes):
		pass

	@QtCore.Slot(QtGui.QColor, QtGui.QColor)
	def setBinColors(self, fg_color:QtGui.QColor, bg_color:QtGui.QColor):

		VARIATION     = 110  # Must be >100 to  have effect
		VARIATION_MID = 105  # Must be >100 to  have effect

		palette = self.palette()

		palette.setColor(QtGui.QPalette.ColorRole.Text,            fg_color)
		palette.setColor(QtGui.QPalette.ColorRole.ButtonText,      fg_color)
		palette.setColor(QtGui.QPalette.ColorRole.Base,            bg_color)
		palette.setColor(QtGui.QPalette.ColorRole.AlternateBase,   bg_color.darker(VARIATION))
		palette.setColor(QtGui.QPalette.ColorRole.Button,          bg_color.darker(VARIATION))

		palette.setColor(QtGui.QPalette.ColorRole.WindowText,      fg_color)
		palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, bg_color.lighter(VARIATION).lighter(VARIATION).lighter(VARIATION))
		palette.setColor(QtGui.QPalette.ColorRole.Window,          bg_color.darker(VARIATION).darker(VARIATION))


		# Fusion scrollbar uses these colors per https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html
		# Although it... like... doesn't? lol
		palette.setColor(QtGui.QPalette.ColorRole.Light,    palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION))      # Lighter than Button color
		palette.setColor(QtGui.QPalette.ColorRole.Midlight, palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION_MID))  # Between Button and Light
		palette.setColor(QtGui.QPalette.ColorRole.Mid,      palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION_MID))   # Between Button and Dark
		palette.setColor(QtGui.QPalette.ColorRole.Dark,     palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION))       # Darker than Button

		self.setPalette(palette)
	
	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, bin_font:QtGui.QFont):
		self._tree_bin_contents.setFont(bin_font)

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
	