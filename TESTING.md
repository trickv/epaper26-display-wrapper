# Testing Documentation

This document describes the testing infrastructure for the e-paper display wrapper project.

## Overview

The test suite includes:
- **Python unit tests** with mocked API calls (no real API access required)
- **BMP generation tests** to verify image rendering
- **C code build tests** for the epaper display driver
- **CI/CD integration** via GitHub Actions

## Quick Start

### Running All Tests Locally

```bash
# Make sure you're in the project directory
cd /path/to/epaper26-display-wrapper

# Run all tests
./run_tests.sh
```

### Running Individual Test Suites

#### Python Unit Tests Only
```bash
pytest tests/test_main.py -v
```

#### C Build Test Only
```bash
bash tests/test_c_build.sh
```

#### Syntax Check Only
```bash
python -m py_compile main.py
```

## Test Details

### Python Tests (`tests/test_main.py`)

These tests verify the BMP generation functionality without requiring real API access or hardware.

**Features:**
- Mocks all HTTP API calls to vanstaveren.us
- Tests both test mode (`--test` flag) and production mode
- Verifies BMP file dimensions (152x296)
- Checks that images contain expected pixel data
- Tests error handling (e.g., unavailable API state)
- Verifies correct room labels ("MBR", "2F")

**Test Cases:**
- `test_bmp_generation`: Verifies BMPs are created with correct properties
- `test_test_mode`: Checks test mode behavior (convert + eog)
- `test_production_mode`: Verifies production mode (copy to buydisplay + run epd)
- `test_api_unavailable`: Tests handling of unavailable API responses
- `test_labels_are_correct`: Ensures correct room labels are used

### C Build Test (`tests/test_c_build.sh`)

Verifies that the C code submodule is properly initialized with all necessary source files.

**What it tests:**
- Submodule is properly initialized
- Makefile exists
- C source files are present (*.c files)
- Attempts compilation (optional - failure is acceptable)

**Important:** This test does **not** require WiringPi or Raspberry Pi hardware. Build failure is expected and acceptable on non-RPi systems, as long as the source files are present. The test verifies repository structure, not compilation success.

## Dependencies

### Python Dependencies
- Main dependencies (in `requirements.txt`):
  - `pytz` - Timezone handling
  - `python-dateutil` - Date parsing
  - `Pillow` - Image generation
  - `filelock` - File locking

- Test dependencies (in `test_requirements.txt`):
  - `pytest` - Test framework
  - `pytest-mock` - Mocking utilities

### System Dependencies
For local development (Ubuntu/Debian):
```bash
sudo apt-get install -y \
    libjpeg-dev \
    fonts-dejavu-core \
    ttf-bitstream-vera \
    build-essential
```

**Note:** `ttf-bitstream-vera` provides the Vera font family required by main.py for rendering text on the e-paper display.

## Continuous Integration

### GitHub Actions Workflow

The CI pipeline (`.github/workflows/ci.yml`) runs on every push and pull request.

**Jobs:**

1. **test-python** (Matrix: Python 3.8, 3.9, 3.10, 3.11)
   - Installs dependencies
   - Runs pytest suite
   - Checks Python syntax

2. **test-c-build**
   - Checks out submodules
   - Installs build tools
   - Runs C build test

3. **lint-python**
   - Runs flake8 for code quality
   - Checks for syntax errors and undefined names

4. **verify-bmp-generation**
   - Generates BMP files in test mode
   - Verifies files are created and non-empty
   - Uploads BMPs as artifacts (retained for 5 days)

## Writing New Tests

### Adding Python Tests

Add test functions to `tests/test_main.py` or create new test files in the `tests/` directory:

```python
def test_my_feature(temp_dir, mock_http, monkeypatch):
    """Test description"""
    # Your test code here
    pass
```

Available fixtures:
- `temp_dir`: Temporary directory for test outputs
- `mock_http`: Mocked HTTP connections
- `mock_subprocess`: Mocked os.system calls
- `monkeypatch`: Pytest's monkeypatch fixture

### Running Specific Tests

```bash
# Run a specific test function
pytest tests/test_main.py::test_bmp_generation -v

# Run tests matching a pattern
pytest tests/ -k "bmp" -v

# Run with verbose output
pytest tests/ -vv
```

## Troubleshooting

### Tests fail with "No module named 'pytest'"
```bash
pip install -r test_requirements.txt
```

### Tests fail with PIL/Pillow errors
```bash
sudo apt-get install libjpeg-dev
pip install --upgrade Pillow
```

### C build test fails
The C build test only requires the submodule and source files to be present. **Build failure is acceptable** since WiringPi is Raspberry Pi-specific. If the test fails completely, ensure git submodules are initialized:
```bash
git submodule update --init --recursive
```
The test will show "⚠ Build failed (this is expected without wiringPi library)" but should still pass.

### Font errors in tests
Install the required font package:
```bash
sudo apt-get install fonts-dejavu-core
```

## Coverage Reports (Optional)

To generate code coverage reports:

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in a browser
```

## Test Outputs

When running tests locally:
- BMP files are generated in temporary directories (cleaned up automatically)
- Test mode artifacts: `combined-testmode.bmp` (gitignored)
- Lock file: `.run-lock` (gitignored)

In GitHub Actions:
- Generated BMPs are uploaded as artifacts
- Available for download from the Actions tab for 5 days
