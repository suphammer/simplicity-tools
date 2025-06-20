#!/usr/bin/env python3
"""
Basic tests for the Simplicity Tools package.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from simplicity_tools import SimplicityTools
from simplicity_tools.exceptions import SimplicityToolsError, PlatformNotSupportedError


class TestSimplicityTools(unittest.TestCase):
    """Test cases for SimplicityTools."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tools = SimplicityTools(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_platform_detection(self):
        """Test platform detection."""
        platform_info = self.tools.get_platform_info()
        
        self.assertIn('system', platform_info)
        self.assertIn('machine', platform_info)
        self.assertIn('architecture', platform_info)
        self.assertIn('python_version', platform_info)
        
        # Check that system is one of the expected values
        self.assertIn(platform_info['system'], ['windows', 'darwin', 'linux'])
    
    def test_platform_support_check(self):
        """Test platform support checking."""
        is_supported = self.tools.is_platform_supported()
        self.assertIsInstance(is_supported, bool)
    
    def test_tool_status(self):
        """Test tool status checking."""
        status = self.tools.get_status()
        
        self.assertIn('platform', status)
        self.assertIn('platform_supported', status)
        self.assertIn('tools_dir', status)
        self.assertIn('tools', status)
        
        # Check that both tools are in the status
        self.assertIn('slc-cli', status['tools'])
        self.assertIn('zap', status['tools'])
        
        # Check tool status structure
        for tool_name, tool_status in status['tools'].items():
            self.assertIn('installed', tool_status)
            self.assertIn('path', tool_status)
            self.assertIsInstance(tool_status['installed'], bool)
    
    def test_tool_installation_check(self):
        """Test tool installation checking."""
        # Initially, tools should not be installed
        self.assertFalse(self.tools.is_tool_installed('slc-cli'))
        self.assertFalse(self.tools.is_tool_installed('zap'))
        
        # Should raise ToolNotFoundError when trying to get path
        with self.assertRaises(Exception):
            self.tools.get_tool_path('slc-cli')
    
    def test_invalid_tool_name(self):
        """Test handling of invalid tool names."""
        with self.assertRaises(ValueError):
            self.tools.is_tool_installed('invalid-tool')
        
        with self.assertRaises(ValueError):
            self.tools.get_tool_path('invalid-tool')
    
    def test_tools_directory_creation(self):
        """Test that tools directory is created."""
        tools_dir = Path(self.temp_dir)
        self.assertTrue(tools_dir.exists())
        self.assertTrue(tools_dir.is_dir())


class TestPlatformDetector(unittest.TestCase):
    """Test cases for PlatformDetector."""
    
    def setUp(self):
        """Set up test environment."""
        from simplicity_tools.platform import PlatformDetector
        self.detector = PlatformDetector()
    
    def test_architecture_normalization(self):
        """Test architecture name normalization."""
        # Test that architecture is normalized
        self.assertIn(self.detector.architecture, ['x64', 'x86', 'arm64', 'arm32'])
    
    def test_executable_names(self):
        """Test executable name generation."""
        # Test slc-cli executable name
        slc_name = self.detector.get_executable_name('slc-cli')
        if self.detector.system == 'windows':
            self.assertEqual(slc_name, 'slc-cli.exe')
        else:
            self.assertEqual(slc_name, 'slc-cli')
        
        # Test zap executable name
        zap_name = self.detector.get_executable_name('zap')
        if self.detector.system == 'windows':
            self.assertEqual(zap_name, 'zap.exe')
        else:
            self.assertEqual(zap_name, 'zap')


if __name__ == '__main__':
    unittest.main() 