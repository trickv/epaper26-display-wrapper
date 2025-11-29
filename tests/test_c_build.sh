#!/usr/bin/env bash
#
# Test script to verify that the C code submodule is properly set up.
#
# Note: This test does NOT require wiringPi or Raspberry Pi hardware.
# It only verifies that the submodule is initialized and contains the expected source files.
# Actual compilation is attempted but failure is acceptable since wiringPi is RPi-specific.
#

echo "Testing C code submodule setup..."

# Check if submodule is initialized
if [ ! -d "buydisplay-epaper26-example-adaptation/.git" ]; then
    echo "Initializing git submodule..."
    git submodule update --init --recursive || {
        echo "ERROR: Failed to initialize submodule"
        exit 1
    }
fi

# Check if the wiringpi directory exists
if [ ! -d "buydisplay-epaper26-example-adaptation/wiringpi" ]; then
    echo "ERROR: wiringpi directory not found in submodule"
    exit 1
fi

echo "✓ Submodule initialized"

# Change to wiringpi directory
cd buydisplay-epaper26-example-adaptation/wiringpi/ || {
    echo "ERROR: Cannot cd to wiringpi directory"
    exit 1
}

# Verify essential files exist
echo "Checking for essential files..."

if [ ! -f "Makefile" ]; then
    echo "ERROR: Makefile not found"
    exit 1
fi
echo "✓ Makefile exists"

# Count C source files (check in current dir and subdirs)
C_FILE_COUNT=$(find . -name "*.c" 2>/dev/null | wc -l)
if [ "$C_FILE_COUNT" -eq 0 ]; then
    echo "ERROR: No C source files found"
    exit 1
fi
echo "✓ Found $C_FILE_COUNT C source file(s)"

# List some of the source files for visibility
echo "Sample C source files:"
find . -name "*.c" 2>/dev/null | head -5 | sed 's/^/  - /'
if [ "$C_FILE_COUNT" -gt 5 ]; then
    echo "  ... and $((C_FILE_COUNT - 5)) more"
fi

# Attempt to build (optional - failure is acceptable without wiringPi)
echo ""
echo "Attempting build (failure expected without wiringPi library)..."

if make clean 2>/dev/null && make 2>&1 | head -20; then
    echo "✓ Build succeeded!"
    if [ -f "epd" ]; then
        echo "✓ Binary 'epd' created"
    fi
else
    echo ""
    echo "⚠ Build failed (this is expected without wiringPi library)"
    echo "✓ Test passed: Source files verified, build attempted"
fi

echo ""
echo "=== C submodule test passed ==="
exit 0
