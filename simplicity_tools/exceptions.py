"""
Custom exceptions for the Simplicity Tools package.
"""


class SimplicityToolsError(Exception):
    """Base exception for all Simplicity Tools errors."""
    pass


class ToolNotFoundError(SimplicityToolsError):
    """Raised when a required tool is not found."""
    pass


class DownloadError(SimplicityToolsError):
    """Raised when downloading a tool fails."""
    pass


class PlatformNotSupportedError(SimplicityToolsError):
    """Raised when the current platform is not supported."""
    pass


class InstallationError(SimplicityToolsError):
    """Raised when installing a tool fails."""
    pass 