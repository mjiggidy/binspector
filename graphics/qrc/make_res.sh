for f in *.qrc; do
	pyside6-rcc "$f" -o "../../src/binspector/res/${f%%qrc}py";
done;