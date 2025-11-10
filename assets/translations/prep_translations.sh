#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR"

shopt -s globstar
pyside6-lupdate ../../src/**/*.py -ts bs.zh_CN.ts