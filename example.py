#!/usr/bin/env python3
"""
Example usage of the Simplicity Tools package.
"""

from simplicity_tools import SimplicityTools
import json


def main():
    """Example usage of SimplicityTools."""
    
    # Initialize the tools manager
    print("Initializing SimplicityTools...")
    tools = SimplicityTools()
    
    # Show platform information
    print("\nPlatform Information:")
    platform_info = tools.get_platform_info()
    for key, value in platform_info.items():
        print(f"  {key}: {value}")
    
    # Check if platform is supported
    print(f"\nPlatform Supported: {tools.is_platform_supported()}")
    
    # Show available versions for each tool
    print("\nAvailable Versions:")
    for tool_name in ['slc-cli', 'zap']:
        versions = tools.get_available_versions(tool_name)
        print(f"  {tool_name}: {', '.join(versions)}")
    
    # Show current status
    print("\nCurrent Status:")
    status = tools.get_status()
    for tool_name, tool_status in status['tools'].items():
        status_str = "✓ Installed" if tool_status['installed'] else "✗ Not installed"
        print(f"  {tool_name}: {status_str}")
        if tool_status['path']:
            print(f"    Path: {tool_status['path']}")
    
    # Ensure tools are installed
    print("\nEnsuring tools are installed...")
    try:
        tools.ensure_tools_installed()
        print("All tools are now installed!")
    except Exception as e:
        print(f"Error installing tools: {e}")
        return
    
    # Example: Run slc-cli --help
    print("\nRunning slc-cli --help:")
    try:
        result = tools.run_slc(['--help'], capture_output=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print("Output:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    except Exception as e:
        print(f"Error running slc-cli: {e}")
    
    # Example: Run zap --version
    print("\nRunning zap --version:")
    try:
        result = tools.run_zap(['--version'], capture_output=True)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print("Output:")
            print(result.stdout.strip())
    except Exception as e:
        print(f"Error running zap: {e}")
    
    # Show final status
    print("\nFinal Status:")
    status = tools.get_status()
    for tool_name, tool_status in status['tools'].items():
        status_str = "✓ Installed" if tool_status['installed'] else "✗ Not installed"
        print(f"  {tool_name}: {status_str}")
        if tool_status['path']:
            print(f"    Path: {tool_status['path']}")


if __name__ == "__main__":
    main() 