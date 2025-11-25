"""
Event filters to handle particular system events 
in a good and nice way that is good and nice
"""

import logging
from PySide6 import QtCore, QtGui

class BSPinchEventFilter(QtCore.QObject):
	"""Handle if the user gets pinchy"""

	sig_user_started_gesture  = QtCore.Signal()
	"""The user has began to pinch"""
	
	sig_user_is_pinching    = QtCore.Signal(float, float)
	"""User is doing a pinchy (`delta since last:float`, `accumulated pinch:float`)"""

	sig_user_finished_gesture = QtCore.Signal()
	"""User has tired of the pinch"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._accumulated_scale     = 0
		self._tracked_gesture_count = 0
	
	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):

		if event.type() != QtCore.QEvent.Type.NativeGesture:
			return False

		# If Begin Native Gesture
		if event.gestureType() == QtCore.Qt.NativeGestureType.BeginNativeGesture:
			
			self.reportPinchBegan()
			return True
			
		# If Actively Zooming
		elif event.gestureType() == QtCore.Qt.NativeGestureType.ZoomNativeGesture:
			
			self.reportPinchUpdated(event)
			return True

		# If End Native Gesture
		elif event.gestureType() == QtCore.Qt.NativeGestureType.EndNativeGesture:
			
			self.reportPinchEnded()
			return True
		
		return False
	
	@QtCore.Slot()
	def reportPinchBegan(self):
		"""User began The Pinch"""

		self._tracked_gesture_count += 1
		logging.getLogger(__name__).debug("Begin gesture, active_gestures=%s", self._tracked_gesture_count)
		
		if self._tracked_gesture_count == 1:
			self.sig_user_started_gesture.emit()

	@QtCore.Slot(object)
	def reportPinchUpdated(self, pinch_event:QtGui.QNativeGestureEvent):
		"""Report the latest accumulated value of The Pinch"""

		self._accumulated_scale += pinch_event.value()
		self.sig_user_is_pinching.emit(pinch_event.value(), self._accumulated_scale)

	@QtCore.Slot()
	def reportPinchEnded(self):

		self._tracked_gesture_count -= 1
		logging.getLogger(__name__).debug("End gesture, active_gestures=%s",self._tracked_gesture_count)
		
		if self._tracked_gesture_count < 1:
			
			self._reset()
			self.sig_user_finished_gesture.emit()
	
	def _reset(self):
		"""Reset tracking values for next pinch"""

		self._tracked_gesture_count = 0
		self._accumulated_scale = 0
		
		logging.getLogger(__name__).debug("Pinch reset")