from PySide6 import QtCore, QtGui, QtWidgets
from ..core.settings import BSStartupBehavior

class BSSettingsPanel(QtWidgets.QWidget):

	sig_use_animations_changed   = QtCore.Signal(bool)
	sig_mob_queue_size_changed   = QtCore.Signal(int)
	sig_startup_behavior_changed = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setLayout(QtWidgets.QFormLayout())

		self._cmb_startup_behavior = QtWidgets.QComboBox()
		self._cmb_startup_behavior.currentIndexChanged.connect(
			lambda: self.sig_startup_behavior_changed.emit(self._cmb_startup_behavior.currentData())
		)
		
		for b in BSStartupBehavior:
			self._cmb_startup_behavior.addItem(b.value, b)

		self._chk_use_animations = QtWidgets.QCheckBox()
		self._chk_use_animations.toggled.connect(self.sig_use_animations_changed)
		
		self._sld_mob_queue      = QtWidgets.QSlider()
		self._sld_mob_queue.valueChanged.connect(self.sig_mob_queue_size_changed)
		self._sld_mob_queue.valueChanged.connect(lambda val: self._sld_mob_queue.setToolTip(str(val)))

		self._sld_mob_queue.setRange(1, 2_000)
		self._sld_mob_queue.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self._sld_mob_queue.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
		self._sld_mob_queue.setTickInterval(500)

		self.layout().addRow(self.tr("On Startup"), self._cmb_startup_behavior)
		self.layout().addRow(self.tr("Use Fancy Animations"), self._chk_use_animations)
		self.layout().addRow(self.tr("Mob Queue Size"), self._sld_mob_queue)
	
	@QtCore.Slot(bool)
	def setUseAnimations(self, use_animations:bool):

		self._chk_use_animations.setChecked(use_animations)
	
	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):

		self._sld_mob_queue.setValue(queue_size)
	
	@QtCore.Slot(object)
	def setStartupBehavior(self, behavior:BSStartupBehavior):

		self._cmb_startup_behavior.setCurrentText(behavior.value)