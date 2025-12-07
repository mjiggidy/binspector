import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.views import binframeview
from binspector.managers import overlaymanager
from binspector.views.overlays import frameruler, framemap

class CoolFrameOverlayView(QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frameview = binframeview.BSBinFrameView()
		
		self._frameview.scene().setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-1000, -1000),
			QtCore.QPointF(1000, 1000)
		))

		self._frameview._overlay_map.setDisplaySize(
			QtCore.QSizeF(300,400)
		)
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))

		self.setCentralWidget(self._frameview)
		
		#self._over_ruler.setRulerSize(24)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())