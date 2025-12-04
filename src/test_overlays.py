import sys
from PySide6 import QtCore, QtGui, QtWidgets
from binspector.views import binframeview
from binspector.managers import overlaymanager
from binspector.views.overlays import frameruler

class CoolFrameOverlayView(QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frameview = binframeview.BSBinFrameView()
		self._over_ruler = frameruler.BSFrameRulerOverlay()
		#self._over_ruler.setRulerOrientations([QtCore.Qt.Orientation.Vertical])
		
		self._frameview.setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-30000, -30000),
			QtCore.QPointF(30000, 30000)
		))
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))
		self._frameview.overlayManager().installOverlay(self._over_ruler)
		self._frameview.sig_view_rect_changed.connect(self.updateRulerTicks)
		
		self.setCentralWidget(self._frameview)
		
		#self._over_ruler.setRulerSize(24)
		

	def resizeEvent(self, event):

		self.updateRulerTicks(self._frameview.viewRect())

		return super().resizeEvent(event)
	
	def updateRulerTicks(self, rect_scene:QtCore.QRect):

		GRID_DIVISIONS     = 3
		GRID_UNIT_SIZE     = QtCore.QSizeF(18,12)

		if QtCore.Qt.Orientation.Horizontal in self._over_ruler.rulerOrientations():
			
			# Align to grid divisions
			range_scene_start = rect_scene.left()  - rect_scene.left()  % GRID_UNIT_SIZE.width()
			range_scene_end  = rect_scene.right()  - rect_scene.right() % GRID_UNIT_SIZE.width() + GRID_UNIT_SIZE.width()
			range_scene_steps = (range_scene_end - range_scene_start) / GRID_UNIT_SIZE.width() + 1

			ticks = []
			
			for step in range(round(range_scene_steps)):

				scene_x = range_scene_start + (GRID_UNIT_SIZE.width() * step)
				viewport_x = self._frameview.mapFromScene(scene_x, 0).x()

				ticks.append(
					frameruler.BSRulerTickInfo(
						ruler_offset = viewport_x,
						tick_label = str(round(scene_x))
					)
				)

			self._over_ruler.setTicks(ticks, QtCore.Qt.Orientation.Horizontal)
		
		if QtCore.Qt.Orientation.Vertical in self._over_ruler.rulerOrientations():

			# Align to grid divisions
			range_scene_start = rect_scene.top() - rect_scene.top() % GRID_UNIT_SIZE.height()
			range_scene_end   = rect_scene.bottom() - rect_scene.bottom() % GRID_UNIT_SIZE.height() + GRID_UNIT_SIZE.height()
			range_scene_steps = (range_scene_end - range_scene_start) / GRID_UNIT_SIZE.height() + 1

			ticks = []

			for step in range(round(range_scene_steps)):

				scene_y = range_scene_start + (GRID_UNIT_SIZE.height() * step)
				viewport_y = self._frameview.mapFromScene(0, scene_y).y()

				ticks.append(
					frameruler.BSRulerTickInfo(
						ruler_offset= viewport_y,
						tick_label = str(round(scene_y))
					)
				)

			self._over_ruler.setTicks(ticks, QtCore.Qt.Orientation.Vertical)




if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())