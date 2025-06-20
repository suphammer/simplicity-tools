#!/usr/bin/env python3
"""
Simple installation script for Simplicity Tools.
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e}")
        if e.stdout:
            print(f"  stdout: {e.stdout}")
        if e.stderr:
            print(f"  stderr: {e.stderr}")
        return False


def main():
    """Main installation function."""
    print("Installing Simplicity Tools...")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Install in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        print("Installation failed!")
        sys.exit(1)
    
    print("\nInstallation completed successfully!")
    print("\nYou can now use the package:")
    print("  python -c \"from simplicity_tools import SimplicityTools; print('Package works!')\"")
    print("  simplicity-tools --help")
    print("  python example.py")


if __name__ == "__main__":
    main() 