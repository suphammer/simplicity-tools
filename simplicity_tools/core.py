"""
Core SimplicityTools class that manages tool installation and execution.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from .platform import PlatformDetector
from .downloader import ToolDownloader
from .exceptions import (
    SimplicityToolsError, 
    ToolNotFoundError, 
    PlatformNotSupportedError,
    InstallationError
)


class SimplicityTools:
    """Main class for managing slc-cli and zap tools."""
    
    def __init__(self, tools_dir: Optional[str] = None):
        """
        Initialize SimplicityTools.
        
        Args:
            tools_dir: Directory to store tools. If None, uses ~/.simplicity-tools
        """
        self.tools_dir = Path(tools_dir) if tools_dir else Path.home() / ".simplicity-tools"
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
        self.platform_detector = PlatformDetector()
        self.downloader = ToolDownloader(str(self.tools_dir))
        
        # Tool configurations
        self.tools = {
            'slc-cli': {
                'executable': self.platform_detector.get_executable_name('slc-cli'),
                'subdir': 'slc-cli'
            },
            'zap': {
                'executable': self.platform_detector.get_executable_name('zap-cli'),
                'subdir': 'zap'
            }
        }
        
        # Cache for tool paths
        self._tool_paths = {}
        
    def get_platform_info(self) -> Dict[str, str]:
        """Get current platform information."""
        return self.platform_detector.get_platform_info()
    
    def is_platform_supported(self) -> bool:
        """Check if the current platform is supported."""
        return self.platform_detector.is_supported()
    
    def _get_tool_path(self, tool_name: str) -> Optional[Path]:
        """Get the path to a tool executable."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Check if we've already found this tool
        if tool_name in self._tool_paths:
            return self._tool_paths[tool_name]
        
        tool_config = self.tools[tool_name]
        executable_name = tool_config['executable']
        subdir = tool_config['subdir']
        
        # Look for the tool in the tools directory
        tool_dir = self.tools_dir / subdir
        if tool_dir.exists():
            executable_path = self.downloader.find_executable_in_dir(tool_dir, executable_name)
            if executable_path and executable_path.exists():
                self._tool_paths[tool_name] = executable_path
                return executable_path
        
        # Check if tool is available in PATH
        if shutil.which(executable_name):
            path_tool = Path(shutil.which(executable_name))
            self._tool_paths[tool_name] = path_tool
            return path_tool
        
        return None
    
    def is_tool_installed(self, tool_name: str) -> bool:
        """Check if a tool is installed."""
        return self._get_tool_path(tool_name) is not None
    
    def get_tool_path(self, tool_name: str) -> Path:
        """Get the path to a tool, raising an error if not found."""
        path = self._get_tool_path(tool_name)
        if path is None:
            raise ToolNotFoundError(f"Tool {tool_name} is not installed")
        return path
    
    def get_slc_path(self) -> Path:
        """Get the path to slc-cli."""
        return self.get_tool_path('slc-cli')
    
    def get_zap_path(self) -> Path:
        """Get the path to zap."""
        return self.get_tool_path('zap')
    
    def install_tool(self, tool_name: str, version: Optional[str] = None) -> Path:
        """Install a specific tool."""
        if not self.is_platform_supported():
            raise PlatformNotSupportedError(
                f"Platform {self.platform_detector.system}-{self.platform_detector.architecture} is not supported"
            )
        
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Get available versions from the URL configuration
        url_config = self.platform_detector._load_url_config()
        if tool_name not in url_config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        available_versions = list(url_config[tool_name].keys())
        
        # Use the first available version if no version is specified
        if version is None:
            version = available_versions[0]  # Use the first (and typically only) version
        
        if version not in available_versions:
            raise ValueError(f"Unknown version '{version}' for tool {tool_name}. Available versions: {available_versions}")
        
        # Check if already installed
        if self.is_tool_installed(tool_name):
            print(f"{tool_name} is already installed")
            return self.get_tool_path(tool_name)
        
        # Get download information
        try:
            download_info = self.platform_detector.get_tool_urls(tool_name, version)
        except Exception as e:
            raise InstallationError(f"Failed to get download info for {tool_name}: {e}")
        
        # Download and extract
        tool_config = self.tools[tool_name]
        executable_name = tool_config['executable']
        
        try:
            executable_path = self.downloader.download_and_extract_tool(
                download_info['url'],
                download_info['filename'],
                tool_name,
                executable_name
            )
            
            # Update cache
            self._tool_paths[tool_name] = executable_path
            return executable_path
            
        except Exception as e:
            raise InstallationError(f"Failed to install {tool_name}: {e}")
    
    def install_all_tools(self) -> Dict[str, Path]:
        """Install all tools."""
        installed_tools = {}
        
        for tool_name in self.tools.keys():
            try:
                path = self.install_tool(tool_name)
                installed_tools[tool_name] = path
            except Exception as e:
                print(f"Warning: Failed to install {tool_name}: {e}")
        
        return installed_tools
    
    def ensure_tools_installed(self) -> None:
        """Ensure all tools are installed, installing them if necessary."""
        for tool_name in self.tools.keys():
            if not self.is_tool_installed(tool_name):
                print(f"Installing {tool_name}...")
                self.install_tool(tool_name)
    
    def run_tool(self, tool_name: str, args: List[str], 
                 capture_output: bool = False, **kwargs) -> subprocess.CompletedProcess:
        """Run a tool with the given arguments."""
        tool_path = self.get_tool_path(tool_name)
        
        cmd = [str(tool_path)] + args
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                **kwargs
            )
            return result
        except subprocess.SubprocessError as e:
            raise SimplicityToolsError(f"Failed to run {tool_name}: {e}")
    
    def run_slc(self, args: List[str], capture_output: bool = False, **kwargs) -> subprocess.CompletedProcess:
        """Run slc-cli with the given arguments."""
        return self.run_tool('slc-cli', args, capture_output, **kwargs)
    
    def run_zap(self, args: List[str], capture_output: bool = False, **kwargs) -> subprocess.CompletedProcess:
        """Run zap with the given arguments."""
        return self.run_tool('zap', args, capture_output, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all tools."""
        status = {
            'platform': self.get_platform_info(),
            'platform_supported': self.is_platform_supported(),
            'tools_dir': str(self.tools_dir),
            'tools': {}
        }
        
        for tool_name in self.tools.keys():
            tool_status = {
                'installed': self.is_tool_installed(tool_name),
                'path': None
            }
            
            if tool_status['installed']:
                try:
                    tool_status['path'] = str(self.get_tool_path(tool_name))
                except ToolNotFoundError:
                    tool_status['installed'] = False
            
            status['tools'][tool_name] = tool_status
        
        return status
    
    def uninstall_tool(self, tool_name: str) -> None:
        """Uninstall a tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_dir = self.tools_dir / self.tools[tool_name]['subdir']
        
        if tool_dir.exists():
            try:
                # Remove all files and subdirectories
                for root, dirs, files in os.walk(tool_dir, topdown=False):
                    for name in files:
                        try:
                            os.remove(os.path.join(root, name))
                        except Exception as e:
                            print(f"Warning: Could not remove file {name}: {e}")
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except Exception as e:
                            print(f"Warning: Could not remove directory {name}: {e}")
                # Now remove the tool directory itself
                try:
                    os.rmdir(tool_dir)
                    print(f"{tool_name} uninstalled successfully")
                except Exception as e:
                    print(f"Warning: Could not remove tool directory {tool_dir}: {e}")
            except Exception as e:
                print(f"Warning: Failed to uninstall {tool_name}: {e}")
        else:
            print(f"{tool_name} is not installed")
        
        # Clear cache
        self._tool_paths.pop(tool_name, None)
    
    def uninstall_all_tools(self) -> None:
        """Uninstall all tools."""
        for tool_name in self.tools.keys():
            self.uninstall_tool(tool_name)
    
    def get_available_versions(self, tool_name: str) -> List[str]:
        """Get available versions for a tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        url_config = self.platform_detector._load_url_config()
        if tool_name not in url_config:
            return []
        
        return list(url_config[tool_name].keys())
    
    def get_installed_version(self, tool_name: str) -> Optional[str]:
        """Get the version of an installed tool (if available)."""
        if not self.is_tool_installed(tool_name):
            return None
        
        # For now, we'll return None as we don't track installed versions
        # This could be enhanced to read version from the tool itself
        return None 