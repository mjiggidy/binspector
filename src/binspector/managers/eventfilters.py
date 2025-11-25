"""
Event filters to handle particular system events 
in a good and nice way that is good and nice
"""

import logging
from PySide6 import QtCore

class BSPinchPanEventFilter(QtCore.QObject):
	"""Handle pinch 'n' pan multitouch events"""
	
	# I peench

	GESTURE_SAMPLE_TIMEOUT_MS = 40
	"""Sample rate (milliseconds) to avoid signal storm"""

	sig_user_started_gesture  = QtCore.Signal(object)
	"""I peench"""
	
	sig_user_is_pinching    = QtCore.Signal(float)
	"""User did a pinchy"""

	sig_user_finished_gesture = QtCore.Signal(object)
	"""User has tired of the pinch"""

	sig_pinch_reset           = QtCore.Signal()

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._pinch_response_curve = QtCore.QEasingCurve()
		self._accumulate = 0
		self._tracked_gesture_count = 0

		self._pinch_response_curve.setType(QtCore.QEasingCurve.Type.InOutQuad)
	
	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):

		if not event.type() == QtCore.QEvent.Type.NativeGesture:
			return super().eventFilter(watched, event)

		# If Begin Native Gesture
		if event.gestureType() == QtCore.Qt.NativeGestureType.BeginNativeGesture:

			
			self._tracked_gesture_count += 1
			logging.getLogger(__name__).debug("Begin gesture=%s, active_gestures=%s", event.gestureType(), self._tracked_gesture_count)
			
			self.sig_user_started_gesture.emit(event.gestureType())
		
		# If End Native Gesture
		elif event.gestureType() == QtCore.Qt.NativeGestureType.EndNativeGesture:
			
			self._tracked_gesture_count -= 1
			logging.getLogger(__name__).debug("End gesture=%s, active_gestures=%s", event.gestureType(), self._tracked_gesture_count)
			

			if not self._tracked_gesture_count:
				
				self.reset()
				self.sig_user_finished_gesture.emit(event.gestureType())
		
		# If Actively Zooming
		elif event.gestureType() == QtCore.Qt.NativeGestureType.ZoomNativeGesture:
		
			self._accumulate += event.value()
			self.reportPinchZoom(self._accumulate)

		return super().eventFilter(watched, event)
	
	@QtCore.Slot()
	def reportPinchZoom(self, zoom_delta:float):

		self.sig_user_is_pinching.emit(zoom_delta)
	
	def reset(self):

		self._tracked_gesture_count = 0
		self._accumulate = 0
		
		logging.getLogger(__name__).debug("Pinch reset")
		self.sig_pinch_reset.emit()