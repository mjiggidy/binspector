from PySide6 import QtGui

def is_dark_mode(palette:QtGui.QPalette) -> bool:
	"""Determine if a palette is "dark" or not"""

	return palette.window().color().lightness() < palette.windowText().color().lightness()

def prep_palette(base_palette:QtGui.QPalette, fg_color:QtGui.QColor, bg_color:QtGui.QColor):
	VARIATION     = 110  # Must be >100 to  have effect
	VARIATION_MID = 105  # Must be >100 to  have effect

	palette = QtGui.QPalette(base_palette)

	palette.setColor(QtGui.QPalette.ColorRole.Text,            fg_color)
	palette.setColor(QtGui.QPalette.ColorRole.ButtonText,      fg_color)
	palette.setColor(QtGui.QPalette.ColorRole.Base,            bg_color)
	palette.setColor(QtGui.QPalette.ColorRole.AlternateBase,   bg_color.darker(VARIATION))
	palette.setColor(QtGui.QPalette.ColorRole.Button,          bg_color.darker(VARIATION))

	palette.setColor(QtGui.QPalette.ColorRole.WindowText,      fg_color)
	palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, bg_color.lighter(VARIATION).lighter(VARIATION).lighter(VARIATION))
	palette.setColor(QtGui.QPalette.ColorRole.Window,          bg_color.darker(VARIATION).darker(VARIATION))


	# Fusion scrollbar uses these colors per https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html
	# Although it... like... doesn't? lol
	palette.setColor(QtGui.QPalette.ColorRole.Light,    palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION).lighter(VARIATION))      # Lighter than Button color
	palette.setColor(QtGui.QPalette.ColorRole.Midlight, palette.color(QtGui.QPalette.ColorRole.Button).lighter(VARIATION_MID))  # Between Button and Light
	palette.setColor(QtGui.QPalette.ColorRole.Mid,      palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION_MID))   # Between Button and Dark
	palette.setColor(QtGui.QPalette.ColorRole.Dark,     palette.color(QtGui.QPalette.ColorRole.Button).darker(VARIATION))       # Darker than Button

	return palette