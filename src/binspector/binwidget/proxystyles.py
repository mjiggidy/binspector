from PySide6 import QtCore, QtWidgets

class BSScrollBarStyle(QtWidgets.QProxyStyle):
	"""Modify scrollbar height"""

	def __init__(self, *args, scale_factor:int|float=1.25, **kwargs):

		super().__init__(*args, **kwargs)
		self._scale_factor = scale_factor

	def pixelMetric(self, metric:QtWidgets.QStyle.PixelMetric, option:QtWidgets.QStyleOption=None, widget:QtWidgets.QWidget=None):
		"""Scroll bar defaults with modified height metrics"""

		if metric == QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent:
			
			return round(
				self.baseStyle().pixelMetric(metric, option, widget) * self._scale_factor
			)
		
		else:
			return self.baseStyle().pixelMetric(metric, option, widget)
		
	@QtCore.Slot(float)
	def setScrollbarScaleFactor(self, scale_factor:float|int):
		
		self._scale_factor = scale_factor