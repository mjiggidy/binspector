import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.views import binframeview
from binspector.managers import overlaymanager
from binspector.views.overlays import frameruler

class CoolFrameOverlayView(QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frameview = binframeview.BSBinFrameView()
		#self._over_ruler = frameruler.BSFrameRulerOverlay()
		#self._over_ruler.setRulerOrientations([QtCore.Qt.Orientation.Vertical])
		
		self._frameview.setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-30000, -30000),
			QtCore.QPointF(30000, 30000)
		))
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))
		#self._frameview.overlayManager().installOverlay(self._over_ruler)
		#self._frameview.sig_view_rect_changed.connect(self.updateRulerTicks)

		#self._frameview.viewport().setMouseTracking(True)
		#self._frameview.viewport().installEventFilter(self)
		
		self.setCentralWidget(self._frameview)
		
		#self._over_ruler.setRulerSize(24)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())