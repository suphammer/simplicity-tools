"""
Platform detection and mapping for Simplicity Tools.
"""

import platform
import sys
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from .exceptions import PlatformNotSupportedError


class PlatformDetector:
    """Detects the current platform and provides mapping to tool URLs."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.architecture = self._normalize_architecture()
        self._url_config = None
        
    def _normalize_architecture(self) -> str:
        """Normalize architecture names."""
        arch_map = {
            'x86_64': 'x64',
            'amd64': 'x64',
            'i386': 'x86',
            'i686': 'x86',
            'aarch64': 'arm64',
            'arm64': 'arm64',
            'armv7l': 'arm32',
            'armv8l': 'arm64',
        }
        return arch_map.get(self.machine, self.machine)
    
    def _load_url_config(self) -> Dict:
        """Load URL configuration from JSON file."""
        if self._url_config is None:
            config_path = Path(__file__).parent / "config" / "tool_urls.json"
            try:
                with open(config_path, 'r') as f:
                    self._url_config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                # Fallback to hardcoded URLs if config file is not available
                self._url_config = self._get_fallback_urls()
        return self._url_config
    
    def _get_fallback_urls(self) -> Dict:
        """Fallback URLs if config file is not available."""
        return {
            'slc-cli': {
                'latest': {
                    'windows-x64': 'https://www.silabs.com/documents/login/software/slc_cli_windows.zip',
                    'windows-x86': 'https://www.silabs.com/documents/login/software/slc_cli_windows.zip',
                    'darwin-x64': 'https://www.silabs.com/documents/login/software/slc_cli_mac.zip',
                    'darwin-arm64': 'https://www.silabs.com/documents/login/software/slc_cli_mac_aarch64.zip',
                    'linux-x64': 'https://www.silabs.com/documents/login/software/slc_cli_linux.zip',
                    'linux-arm64': 'https://www.silabs.com/documents/login/software/slc_cli_linux.zip',
                    'linux-arm32': 'https://www.silabs.com/documents/login/software/slc_cli_linux.zip',
                }
            },
            'zap': {
                'v2025.05.07': {
                    'windows-x64': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-windows-x64.zip',
                    'windows-x86': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-windows-x86.zip',
                    'darwin-x64': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-mac-x64.zip',
                    'darwin-arm64': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-mac-arm64.zip',
                    'linux-x64': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-linux-x64.zip',
                    'linux-arm64': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-linux-arm64.zip',
                    'linux-arm32': 'https://github.com/project-chip/zap/releases/download/v2025.05.07/zap-linux-arm32.zip',
                }
            }
        }
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get current platform information."""
        return {
            'system': self.system,
            'machine': self.machine,
            'architecture': self.architecture,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
        }
    
    def is_supported(self) -> bool:
        """Check if the current platform is supported."""
        supported_platforms = [
            ('windows', 'x64'),
            ('windows', 'x86'),
            ('darwin', 'x64'),
            ('darwin', 'arm64'),
            ('linux', 'x64'),
            ('linux', 'arm64'),
            ('linux', 'arm32'),
        ]
        return (self.system, self.architecture) in supported_platforms
    
    def get_tool_urls(self, tool_name: str, version: str = "latest") -> Dict[str, str]:
        """Get download URLs for tools based on platform."""
        if not self.is_supported():
            raise PlatformNotSupportedError(
                f"Platform {self.system}-{self.architecture} is not supported"
            )
        
        url_config = self._load_url_config()
        platform_key = f"{self.system}-{self.architecture}"
        
        if tool_name not in url_config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        if version not in url_config[tool_name]:
            raise ValueError(f"Unknown version: {version} for tool {tool_name}")
        
        if platform_key not in url_config[tool_name][version]:
            raise PlatformNotSupportedError(
                f"Platform {platform_key} not supported for {tool_name} version {version}"
            )
        
        url = url_config[tool_name][version][platform_key]
        return {
            'url': url,
            'platform': platform_key,
            'filename': url.split('/')[-1]
        }
    
    def get_executable_name(self, tool_name: str) -> str:
        """Get the executable name for a tool on the current platform."""
        if self.system == 'windows':
            return f"{tool_name}.exe"
        return tool_name 