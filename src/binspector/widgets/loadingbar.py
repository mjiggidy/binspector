from PySide6 import QtCore, QtGui, QtWidgets

class BSProgressBar(QtWidgets.QProgressBar):
	"""A progress bar with state and animation and blow"""

	_STATUS_LOADING_PROPERTIES = QtWidgets.QApplication.tr("Loading bin properties...")
	_STATUS_LOADING_MOBS       = QtWidgets.QApplication.tr("Loading %v of %m mobs", "%v=current_count; %m=total_count")

	sig_enable_animation_changed = QtCore.Signal(bool)

	def __init__(self, *args, animation_enabled:bool=True, start_hidden:bool=True, **kwargs):

		super().__init__(*args, **kwargs)

		policy = self.sizePolicy()
		policy.setRetainSizeWhenHidden(True)
		self.setSizePolicy(policy)
		
		self._anim_enabled = animation_enabled

		self._anim_progress = QtCore.QVariantAnimation(parent=self)
		self._anim_progress.setStartValue(0)
		self._anim_progress.setEndValue(0)
		self._anim_progress.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
		
		self._anim_progress.valueChanged.connect(self.setValue)

		self._timer_chunk = QtCore.QElapsedTimer()

		if start_hidden:
			self.hide()


	@QtCore.Slot(int)
	def accumulateLoadedBinMobsCount(self, additional_mobs_count:int):
		"""Add an additional number of mobs to the current mob count"""

		if not self._anim_enabled:

			self.setValue(self.value() + additional_mobs_count)
			return
		
		last_duration = self._timer_chunk.restart() if self._timer_chunk.isValid() else 5_000
		
		#adj_duration  = round(last_duration * (additional_mobs_count / self.maximum())) if self.maximum() else last_duration
		adj_duration = last_duration

		new_end = min(self._anim_progress.endValue() + additional_mobs_count, self.maximum())
		
		print("Old end was ", self._anim_progress.endValue())
		print("New end is ", new_end)
		print("Duration was ", last_duration)

		self._anim_progress.stop()
		self._anim_progress.setStartValue(self._anim_progress.endValue())
		self._anim_progress.setEndValue(new_end)
		self._anim_progress.setDuration(adj_duration)

		if not self._timer_chunk.isValid():
			self._timer_chunk.start()
		
		self._anim_progress.start()
	
	@QtCore.Slot(bool)
	def setEnableAnimation(self, enable_animation:bool):
		"""Enable animated transitions between progress updates"""

		if self._anim_enabled == enable_animation:
			return
		
		self._anim_enabled = enable_animation

		self.sig_enable_animation_changed.emit(enable_animation)

	def animationEnabled(self) -> bool:
		"""Are animated transitions between progress updates enabled"""

		return self._anim_enabled
	
	@QtCore.Slot()
	def startLoadingBinProperties(self):

		self.setFormat(self._STATUS_LOADING_PROPERTIES)
		self.setMaximum(0)
		self.show()

	@QtCore.Slot(int, int)
	def startLoadingBinMobs(self, total_mob_count:int, queue_size:int):


		self.setValue(0)
		self.setMaximum(total_mob_count)
		self.setFormat(self._STATUS_LOADING_MOBS)

		self._anim_progress.stop()
		self._anim_progress.setStartValue(0)
		self._anim_progress.setEndValue(0)

	#	self.accumulateLoadedBinMobsCount(min(queue_size, total_mob_count))

		self.show()

	@QtCore.Slot()
	def stop(self):

		self._anim_progress.stop()
		self._timer_chunk.invalidate()

		self.hide()
		self.setValue(0)
		self.setMaximum(0)