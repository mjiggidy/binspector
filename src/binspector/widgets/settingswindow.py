from PySide6 import QtCore, QtGui, QtWidgets

class BSSettingsPanel(QtWidgets.QWidget):

	sig_use_animations_changed = QtCore.Signal(bool)
	sig_mob_queue_size_changed = QtCore.Signal(int)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setLayout(QtWidgets.QFormLayout())

		self._chk_use_animations = QtWidgets.QCheckBox()
		self._chk_use_animations.toggled.connect(self.sig_use_animations_changed)
		
		self._sld_mob_queue      = QtWidgets.QSlider()
		self._sld_mob_queue.valueChanged.connect(self.sig_mob_queue_size_changed)

		self._sld_mob_queue.setRange(1, 10_000)
		self._sld_mob_queue.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self._sld_mob_queue.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)

		self.layout().addRow("Use Fancy Animations", self._chk_use_animations)
		self.layout().addRow("Mob Queue Size", self._sld_mob_queue)
	
	@QtCore.Slot(bool)
	def setUseAnimations(self, use_animations:bool):

		self._chk_use_animations.setChecked(use_animations)
	
	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):

		self._sld_mob_queue.setValue(queue_size)