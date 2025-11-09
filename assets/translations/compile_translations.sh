for f in *.ts; do
	pyside6-lrelease "$f" -qm "${f%.ts}.qm"
done;