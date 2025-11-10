#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"

for f in *.ts; do
	pyside6-lrelease "$f" -qm "${f%.ts}.qm"
done;