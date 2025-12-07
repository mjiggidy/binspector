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
		
		self._frameview.scene().setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-500, -500),
			QtCore.QPointF(1000, 1000)
		))
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))

		#self._frameview._overlay_map.setSceneRect(self._frameview.sceneRect())
		#self._frameview.sig_view_rect_changed.connect(self._frameview._overlay_map.setVisibleRect)
		self._frameview._overlay_map.setMapDisplayAlignment(QtCore.Qt.AlignmentFlag.AlignBottom|QtCore.Qt.AlignmentFlag.AlignLeft)
		self.setCentralWidget(self._frameview)
		
		#self._over_ruler.setRulerSize(24)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())