import sys
from PySide6 import QtCore, QtWidgets
from binspector.widgets import loadingbar

class ProgressTester(QtWidgets.QWidget):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._progbar = loadingbar.BSProgressBar(animation_enabled=True, start_hidden=False)

		self.layout().addWidget(self._progbar)

		self._btn_load_properties = QtWidgets.QPushButton("Start Load Properties")
		self._btn_start_mobs      = QtWidgets.QPushButton("Start Load Mobs")
		self._btn_add_mobs        = QtWidgets.QPushButton("Load More Mobs")
		self._btn_stop            = QtWidgets.QPushButton("Stop")

		self._btn_load_properties.clicked.connect(self._progbar.startLoadingBinProperties)
		self._btn_start_mobs.clicked.connect(self.startMobs)
		self._btn_add_mobs.clicked.connect(self.addMobs)
		self._btn_stop.clicked.connect(self._progbar.stop)

		btn_layout = QtWidgets.QHBoxLayout()

		btn_layout.addWidget(self._btn_load_properties)
		btn_layout.addWidget(self._btn_start_mobs)
		btn_layout.addWidget(self._btn_add_mobs)
		btn_layout.addWidget(self._btn_stop)
		
		self.layout().addLayout(btn_layout)

	@QtCore.Slot()
	def startMobs(self):

		self._progbar.startLoadingBinMobs(12500, 50)
	
	@QtCore.Slot()
	def addMobs(self):

		self._progbar.accumulateLoadedBinMobsCount(500)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = ProgressTester()
	wnd.show()

	sys.exit(app.exec())