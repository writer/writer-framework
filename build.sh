#!/bin/bash

# The script fails if any step fails
set -e

# UI BUILD

cd ./ui
npm run build
cd ..

# PYTEST

cd ./tests
pytest
cd ..

# TYPE CHECKS (MYPY)

mypy ./src/streamsync/*.py

# APP PROVISIONING

rm -rf ./src/streamsync/app_templates/*
cp -r ./apps/default ./src/streamsync/app_templates
cp -r ./apps/hello ./src/streamsync/app_templates

# PYTHON PACKAGE BUILD

rm -rf ./dist/*
python -m build