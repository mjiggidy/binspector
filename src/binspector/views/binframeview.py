from PySide6 import QtWidgets

class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

