#!/bin/bash

# Script to run the presenter
# Usage: ./presenter.sh
# Example: ./presenter.sh

SCRIPT_DIR="/Users/andrzejkowal/projects/ISO-21-document-mapping-maching-agent"
VENV_PYTHON="${SCRIPT_DIR}/.venv/bin/python"
PYTHON_SCRIPT="${SCRIPT_DIR}/app/visual/presenter.py"

# Check if virtual environment Python exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found at $VENV_PYTHON"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Change to script directory to ensure relative paths work correctly
cd "$SCRIPT_DIR" || exit 1

# Add main project directory to Python path
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Execute the Python script
"$VENV_PYTHON" "$PYTHON_SCRIPT"

