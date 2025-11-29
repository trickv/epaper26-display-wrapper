#!/usr/bin/env python
"""
Test suite for the e-paper display wrapper.
Tests BMP generation with mocked API responses.
"""

import os
import sys
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import tempfile
import shutil

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockHTTPResponse:
    """Mock HTTP response object"""
    def __init__(self, data):
        self.data = data

    def read(self):
        return json.dumps(self.data).encode('utf-8')


class MockHTTPSConnection:
    """Mock HTTPS connection that returns predefined responses"""

    # Define mock responses for different endpoints
    MOCK_RESPONSES = {
        "/~trick/epaper/now-ac-power.cgi": {"state": "1234.5"},
        "/~trick/epaper/solaredge-today.cgi": {"state": "15678.9"},
        "/~trick/epaper/hass-tde-projection.cgi": {"state": "12.5"},
        "/~trick/epaper/hass-ecobee-br-sensor.cgi": {"state": "72.0"},
        "/~trick/epaper/hass-ecobee-cj-sensor.cgi": {"state": "70.0"},
        "/~trick/epaper/hass-heat-load-east.cgi": {"state": "45"},
        "/~trick/epaper/hass-heat-load-west.cgi": {"state": "38"},
        "/~trick/epaper/hass-heat-load-forced-air.cgi": {"state": "12"},
        "/~trick/epaper/hass-boiler-set-point.cgi": {"state": "150"},
        "/~trick/epaper/my-current-net-metering.cgi": {
            "state": "123.4",
            "last_updated": "2023-01-01T12:00:00+00:00"
        },
        "/~trick/epaper/hass-net-last-update.cgi": {"state": "0.5"},
    }

    def __init__(self, host):
        self.host = host
        self.endpoint = None

    def request(self, method, endpoint):
        self.endpoint = endpoint

    def getresponse(self):
        response_data = self.MOCK_RESPONSES.get(
            self.endpoint,
            {"state": "0"}
        )
        return MockHTTPResponse(response_data)

    def close(self):
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_http():
    """Mock HTTP connections to avoid real API calls"""
    with patch('http.client.HTTPSConnection', MockHTTPSConnection):
        yield


@pytest.fixture
def mock_subprocess():
    """Mock os.system to avoid actually running system commands"""
    with patch('os.system') as mock:
        yield mock




def create_test_globals():
    """Create a globals dict for exec() with all necessary imports"""
    import builtins

    # Start with builtins
    test_globals = {'__builtins__': builtins}

    # Import real modules that we need
    test_globals['os'] = __import__('os')
    test_globals['datetime'] = __import__('datetime')
    test_globals['dateutil'] = __import__('dateutil')
    test_globals['pytz'] = __import__('pytz')
    test_globals['argparse'] = __import__('argparse')
    test_globals['json'] = __import__('json')
    test_globals['http'] = __import__('http')

    # Import PIL modules
    from PIL import Image, ImageDraw, ImageFont
    test_globals['Image'] = Image
    test_globals['ImageDraw'] = ImageDraw
    test_globals['ImageFont'] = ImageFont

    # Import filelock
    from filelock import FileLock, Timeout
    test_globals['FileLock'] = FileLock
    test_globals['Timeout'] = Timeout

    return test_globals


def test_bmp_generation(temp_dir, mock_http, mock_subprocess, monkeypatch):
    """Test that BMP files are generated with correct properties"""

    # Change to temp directory
    original_dir = os.getcwd()
    monkeypatch.chdir(temp_dir)

    # Mock sys.argv to avoid test mode
    with patch('sys.argv', ['main.py']):
        # Import and run main (will be mocked)
        test_globals = create_test_globals()
        exec(open(os.path.join(original_dir, 'main.py')).read(), test_globals)

    # Check that BMP files were created
    assert os.path.exists('black.bmp'), "black.bmp should be generated"
    assert os.path.exists('red.bmp'), "red.bmp should be generated"

    # Verify BMP file properties
    black_img = Image.open('black.bmp')
    red_img = Image.open('red.bmp')

    # Check dimensions (152x296 from main.py)
    assert black_img.size == (152, 296), f"Expected size (152, 296), got {black_img.size}"
    assert red_img.size == (152, 296), f"Expected size (152, 296), got {red_img.size}"

    # Check mode (should be 1-bit)
    assert black_img.mode == '1', f"Expected mode '1', got {black_img.mode}"
    assert red_img.mode == '1', f"Expected mode '1', got {red_img.mode}"

    # Verify files are not empty (should have some black pixels)
    black_pixels = list(black_img.getdata())
    red_pixels = list(red_img.getdata())

    # At least some pixels should be black (0)
    assert 0 in black_pixels, "Black image should have some black pixels"
    assert 0 in red_pixels, "Red image should have some red pixels"

    monkeypatch.chdir(original_dir)


def test_test_mode(temp_dir, mock_http, monkeypatch):
    """Test that test mode generates combined BMP"""

    original_dir = os.getcwd()
    monkeypatch.chdir(temp_dir)

    # Mock os.system to capture commands
    system_calls = []
    def mock_system(cmd):
        system_calls.append(cmd)
        return 0

    with patch('sys.argv', ['main.py', '--test']):
        with patch('os.system', mock_system):
            test_globals = create_test_globals()
            exec(open(os.path.join(original_dir, 'main.py')).read(), test_globals)

    # In test mode, should call convert and eog
    assert any('convert' in call for call in system_calls), \
        "Test mode should call convert to combine images"
    assert any('eog' in call for call in system_calls), \
        "Test mode should call eog to display image"

    # Should NOT copy to buydisplay directory in test mode
    assert not any('buydisplay' in call for call in system_calls), \
        "Test mode should not copy to buydisplay directory"

    monkeypatch.chdir(original_dir)


def test_production_mode(temp_dir, mock_http, monkeypatch):
    """Test that production mode copies files and runs epd"""

    original_dir = os.getcwd()
    monkeypatch.chdir(temp_dir)

    # Create the expected directory structure
    os.makedirs('buydisplay-epaper26-example-adaptation/wiringpi/pic', exist_ok=True)

    system_calls = []
    def mock_system(cmd):
        system_calls.append(cmd)
        return 0

    with patch('sys.argv', ['main.py']):
        with patch('os.system', mock_system):
            test_globals = create_test_globals()
            exec(open(os.path.join(original_dir, 'main.py')).read(), test_globals)

    # In production mode, should copy files
    assert any('cp black.bmp' in call for call in system_calls), \
        "Production mode should copy black.bmp"
    assert any('cp red.bmp' in call for call in system_calls), \
        "Production mode should copy red.bmp"
    assert any('./epd' in call for call in system_calls), \
        "Production mode should run epd binary"

    # Should NOT use convert or eog in production
    assert not any('convert' in call for call in system_calls), \
        "Production mode should not use convert"
    assert not any('eog' in call for call in system_calls), \
        "Production mode should not use eog"

    monkeypatch.chdir(original_dir)


def test_api_unavailable(temp_dir, monkeypatch):
    """Test handling when API returns unavailable state"""

    class UnavailableMockConnection(MockHTTPSConnection):
        MOCK_RESPONSES = {
            "/~trick/epaper/now-ac-power.cgi": {"state": "unavailable"},
            "/~trick/epaper/solaredge-today.cgi": {"state": "12345.6"},
            "/~trick/epaper/hass-tde-projection.cgi": {"state": "10.0"},
            "/~trick/epaper/hass-ecobee-br-sensor.cgi": {"state": "70.0"},
            "/~trick/epaper/hass-ecobee-cj-sensor.cgi": {"state": "68.0"},
            "/~trick/epaper/hass-heat-load-east.cgi": {"state": "40"},
            "/~trick/epaper/hass-heat-load-west.cgi": {"state": "35"},
            "/~trick/epaper/hass-heat-load-forced-air.cgi": {"state": "10"},
            "/~trick/epaper/hass-boiler-set-point.cgi": {"state": "145"},
            "/~trick/epaper/my-current-net-metering.cgi": {
                "state": "100.0",
                "last_updated": "2023-01-01T12:00:00+00:00"
            },
            "/~trick/epaper/hass-net-last-update.cgi": {"state": "1.5"},
        }

    original_dir = os.getcwd()
    monkeypatch.chdir(temp_dir)

    def mock_system(cmd):
        return 0

    with patch('sys.argv', ['main.py', '--test']):
        with patch('http.client.HTTPSConnection', UnavailableMockConnection):
            with patch('os.system', mock_system):
                # Should not raise an exception
                test_globals = create_test_globals()
                exec(open(os.path.join(original_dir, 'main.py')).read(), test_globals)

    # Files should still be created
    assert os.path.exists('black.bmp')
    assert os.path.exists('red.bmp')

    monkeypatch.chdir(original_dir)


def test_labels_are_correct(temp_dir, mock_http, monkeypatch):
    """Test that the correct labels (MBR, 2F) are being used"""

    original_dir = os.getcwd()
    monkeypatch.chdir(temp_dir)

    # Read the source code to verify labels
    with open(os.path.join(original_dir, 'main.py'), 'r') as f:
        source_code = f.read()

    # Verify the labels are correct
    assert '"2F:"' in source_code, "Should use '2F:' label"
    assert '"MBR:"' in source_code, "Should use 'MBR:' label"

    # Verify old labels are not present
    assert '"Office:"' not in source_code, "Should not use 'Office:' label"
    assert '"Guest:"' not in source_code, "Should not use 'Guest:' label"

    monkeypatch.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
