#!/bin/bash

# Script to select documents for a given ISO 27001 control
# Usage: ./select_documents.sh <control_id>
# Example: ./select_documents.sh 5.2

# Check if control number is provided
if [ -z "$1" ]; then
    echo "Error: Control number is required"
    echo "Usage: $0 <control_id>"
    echo "Example: $0 5.2"
    exit 1
fi

CONTROL_ID="$1"
SCRIPT_DIR="/Users/andrzejkowal/projects/ISO-21-document-mapping-maching-agent"
VENV_PYTHON="${SCRIPT_DIR}/.venv/bin/python"
PYTHON_SCRIPT="${SCRIPT_DIR}/app/selector/execute_control.py"

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

# Execute the Python script with the control ID
"$VENV_PYTHON" "$PYTHON_SCRIPT" "$CONTROL_ID"

