import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.frameview import frameview
from binspector.overlays import manager
from binspector.overlays import frameruler, framemap



class CoolFrameOverlayView(QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frameview = frameview.BSBinFrameView()
		
		self._frameview.scene().setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-100, -100),
			QtCore.QSizeF(1000, 500)
		))

		self._frameview._overlay_map.setThumbnailSize(
			QtCore.QSizeF(300,400)
		)
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))
		self._frameview._overlay_map._setEnabled(True)

		self._frameview._overlay_map.sig_view_reticle_panned.connect(self.setCenterPoint)

		self.setCentralWidget(self._frameview)
		

#		self.slider = QtWidgets.QSlider()
#		self.slider.show()
#		self.slider.setRange(0, self._frameview.rect().width())
#		self.slider.valueChanged.connect(lambda x: self._frameview._overlay_map.setThumbnailOffset(
#			QtCore.QPointF(x, 100)
#		))
		
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