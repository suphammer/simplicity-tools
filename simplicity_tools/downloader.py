"""
Download and extraction functionality for Simplicity Tools.
"""

import os
import zipfile
import tarfile
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Callable
import requests
from tqdm import tqdm

from .exceptions import DownloadError, InstallationError


class ToolDownloader:
    """Handles downloading and extracting tools."""
    
    def __init__(self, download_dir: Optional[str] = None):
        self.download_dir = Path(download_dir) if download_dir else Path.home() / ".simplicity-tools"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def download_file(self, url: str, filename: str, progress_callback: Optional[Callable] = None) -> Path:
        """Download a file with progress tracking."""
        file_path = self.download_dir / filename
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                                if progress_callback:
                                    progress_callback(pbar.n, total_size)
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            return file_path
            
        except requests.RequestException as e:
            raise DownloadError(f"Failed to download {url}: {e}")
    
    def extract_archive(self, archive_path: Path, extract_dir: Path) -> None:
        """Extract an archive file (zip or tar.gz)."""
        try:
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.suffix == '.gz' and archive_path.stem.endswith('.tar'):
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
            elif archive_path.suffix == '.tar':
                with tarfile.open(archive_path, 'r') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                raise InstallationError(f"Unsupported archive format: {archive_path.suffix}")
                
        except (zipfile.BadZipFile, tarfile.ReadError) as e:
            raise InstallationError(f"Failed to extract {archive_path}: {e}")
    
    def make_executable(self, file_path: Path) -> None:
        """Make a file executable (Unix-like systems only)."""
        if os.name != 'nt':  # Not Windows
            try:
                os.chmod(file_path, 0o755)
            except OSError as e:
                raise InstallationError(f"Failed to make {file_path} executable: {e}")
    
    def find_executable_in_dir(self, directory: Path, executable_name: str) -> Optional[Path]:
        """Find an executable in a directory."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == executable_name:
                    return Path(root) / file
        return None
    
    def cleanup_archive(self, archive_path: Path) -> None:
        """Clean up downloaded archive file."""
        try:
            if archive_path.exists():
                archive_path.unlink()
        except OSError:
            pass  # Ignore cleanup errors
    
    def download_and_extract_tool(self, url: str, filename: str, tool_name: str, 
                                 executable_name: str) -> Path:
        """Download and extract a tool, returning the path to the executable."""
        print(f"Downloading {tool_name}...")
        
        # Download the archive
        archive_path = self.download_file(url, filename)
        
        # Create extraction directory
        extract_dir = self.download_dir / tool_name
        extract_dir.mkdir(exist_ok=True)
        
        try:
            # Extract the archive
            print(f"Extracting {tool_name}...")
            self.extract_archive(archive_path, extract_dir)
            
            # Find the executable
            executable_path = self.find_executable_in_dir(extract_dir, executable_name)
            if not executable_path:
                raise InstallationError(f"Could not find {executable_name} in extracted files")
            
            # Make executable
            self.make_executable(executable_path)
            
            print(f"{tool_name} installed successfully at {executable_path}")
            return executable_path
            
        finally:
            # Clean up the archive
            self.cleanup_archive(archive_path) 