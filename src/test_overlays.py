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
			QtCore.QPointF(-100, -100),
			QtCore.QSizeF(1000, 500)
		))

		self._frameview._overlay_map.setThumbnailSize(
			QtCore.QSizeF(300,400)
		)
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))

		self._frameview._overlay_map.sig_view_reticle_panned.connect(self.setCenterPoint)
		#self._frameview.set

		self.setCentralWidget(self._frameview)
		
	@QtCore.Slot(object)
	def setCenterPoint(self, center_point:QtCore.QPointF):

		print(center_point)

		self._frameview.centerOn(center_point)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())