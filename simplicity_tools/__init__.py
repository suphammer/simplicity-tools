"""
Simplicity Tools - A Python wrapper for slc-cli and zap tools.
"""

from .core import SimplicityTools
from .exceptions import SimplicityToolsError, ToolNotFoundError, DownloadError

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "SimplicityTools",
    "SimplicityToolsError", 
    "ToolNotFoundError",
    "DownloadError"
] 