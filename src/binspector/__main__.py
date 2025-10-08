import logging
from PySide6 import QtWidgets
from os import PathLike

def main(bin_paths:list[PathLike]) -> int:
	logging.getLogger(__name__).debug("Launching with args: %s", bin_paths)
	app = QtWidgets.QApplication()
	return app.exec()
	

if __name__ == "__main__":
	import sys
	sys.exit(main(sys.argv[1:]))