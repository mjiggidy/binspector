import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.views import binframeview
from binspector.managers import overlaymanager
from binspector.views.overlays import frameruler, framemap

class CoolFrameOverlayView(QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frameview = binframeview.BSBinFrameView()
		#self._over_ruler = frameruler.BSFrameRulerOverlay()
		#self._over_ruler.setRulerOrientations([QtCore.Qt.Orientation.Vertical])
		
		self._frameview.setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-10000, -30000),
			QtCore.QPointF(10000, 30000)
		))
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))

		self._frameview._overlay_map.setSceneRect(self._frameview.sceneRect())
		
		self.setCentralWidget(self._frameview)
		
		#self._over_ruler.setRulerSize(24)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())