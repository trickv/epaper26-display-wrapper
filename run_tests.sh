#!/usr/bin/env bash
#
# Convenience script to run all tests locally
#

set -e

echo "========================================="
echo "Running E-Paper Display Wrapper Test Suite"
echo "========================================="
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Not in a virtual environment"
    echo "Consider running: source ./activate"
    echo ""
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import pytest" 2>/dev/null || {
    echo "Installing test dependencies..."
    pip install -r test_requirements.txt
}

python -c "import PIL" 2>/dev/null || {
    echo "Installing main dependencies..."
    pip install -r requirements.txt
}

echo ""
echo "========================================="
echo "1. Running Python tests"
echo "========================================="
pytest tests/test_main.py

echo ""
echo "========================================="
echo "2. Testing C code build"
echo "========================================="
bash tests/test_c_build.sh

echo ""
echo "========================================="
echo "3. Checking Python syntax"
echo "========================================="
python -m py_compile main.py
echo "✓ main.py syntax OK"

echo ""
echo "========================================="
echo "All tests passed! ✓"
echo "========================================="
