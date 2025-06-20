"""
Command-line interface for Simplicity Tools.
"""

import sys
import json
from typing import List
import click
import os
from pathlib import Path

from .core import SimplicityTools
from .exceptions import SimplicityToolsError, ToolNotFoundError, PlatformNotSupportedError


@click.group()
@click.version_option()
def main():
    """Simplicity Tools - A Python wrapper for slc-cli and zap tools."""
    pass


@main.command()
@click.option('--tools-dir', help='Directory to install tools')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
def status(tools_dir, json_output):
    """Show status of installed tools."""
    try:
        tools = SimplicityTools(tools_dir)
        status_info = tools.get_status()
        
        if json_output:
            click.echo(json.dumps(status_info, indent=2))
        else:
            click.echo("Platform Information:")
            for key, value in status_info['platform'].items():
                click.echo(f"  {key}: {value}")
            
            click.echo(f"\nPlatform Supported: {status_info['platform_supported']}")
            click.echo(f"Tools Directory: {status_info['tools_dir']}")
            
            click.echo("\nTool Status:")
            for tool_name, tool_status in status_info['tools'].items():
                status_str = "✓ Installed" if tool_status['installed'] else "✗ Not installed"
                click.echo(f"  {tool_name}: {status_str}")
                if tool_status['path']:
                    click.echo(f"    Path: {tool_status['path']}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('tool', type=click.Choice(['slc-cli', 'zap', 'all']))
@click.option('--version', help='Tool version to install (uses default from config if not specified)')
@click.option('--tools-dir', help='Directory to install tools')
def install(tool, version, tools_dir):
    """Install tools."""
    try:
        tools = SimplicityTools(tools_dir)
        
        if not tools.is_platform_supported():
            click.echo(f"Error: Platform not supported", err=True)
            sys.exit(1)
        
        if tool == 'all':
            installed = tools.install_all_tools()
            click.echo(f"Installed {len(installed)} tools")
        else:
            # Show available versions if not specified
            if version is None:
                available_versions = tools.get_available_versions(tool)
                if available_versions:
                    click.echo(f"Available versions for {tool}: {', '.join(available_versions)}")
                    click.echo(f"Installing {tool} with version: {available_versions[0]}")
            
            path = tools.install_tool(tool, version)
            click.echo(f"{tool} installed at {path}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('tool', type=click.Choice(['slc-cli', 'zap', 'all']))
@click.option('--tools-dir', help='Directory to install tools')
def uninstall(tool, tools_dir):
    """Uninstall tools."""
    try:
        tools = SimplicityTools(tools_dir)
        
        if tool == 'all':
            tools.uninstall_all_tools()
            click.echo("All tools uninstalled")
        else:
            tools.uninstall_tool(tool)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('--tools-dir', help='Directory to install tools')
@click.option('--capture-output', is_flag=True, help='Capture output instead of displaying it')
def slc(args, tools_dir, capture_output):
    """Run slc-cli with the given arguments."""
    try:
        tools = SimplicityTools(tools_dir)
        tools.ensure_tools_installed()
        
        result = tools.run_slc(list(args), capture_output=capture_output)
        
        if capture_output:
            click.echo(json.dumps({
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }))
        else:
            if result.stdout:
                click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr, err=True)
            sys.exit(result.returncode)
    
    except ToolNotFoundError:
        click.echo("Error: slc-cli not found. Run 'simplicity-tools install slc-cli' first.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('--tools-dir', help='Directory to install tools')
@click.option('--capture-output', is_flag=True, help='Capture output instead of displaying it')
def zap(args, tools_dir, capture_output):
    """Run zap with the given arguments."""
    try:
        tools = SimplicityTools(tools_dir)
        tools.ensure_tools_installed()
        
        result = tools.run_zap(list(args), capture_output=capture_output)
        
        if capture_output:
            click.echo(json.dumps({
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }))
        else:
            if result.stdout:
                click.echo(result.stdout)
            if result.stderr:
                click.echo(result.stderr, err=True)
            sys.exit(result.returncode)
    
    except ToolNotFoundError:
        click.echo("Error: zap not found. Run 'simplicity-tools install zap' first.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--tools-dir', help='Directory to install tools')
def info(tools_dir):
    """Show detailed information about the environment."""
    try:
        tools = SimplicityTools(tools_dir)
        
        click.echo("Simplicity Tools Information")
        click.echo("=" * 30)
        
        # Platform info
        platform_info = tools.get_platform_info()
        click.echo("\nPlatform:")
        for key, value in platform_info.items():
            click.echo(f"  {key}: {value}")
        
        # Support status
        click.echo(f"\nPlatform Supported: {tools.is_platform_supported()}")
        
        # Tools directory
        click.echo(f"Tools Directory: {tools.tools_dir}")
        
        # Tool details
        click.echo("\nTools:")
        for tool_name, tool_config in tools.tools.items():
            click.echo(f"  {tool_name}:")
            click.echo(f"    Executable: {tool_config['executable']}")
            click.echo(f"    Version: {tool_config['version']}")
            click.echo(f"    Installed: {tools.is_tool_installed(tool_name)}")
            
            if tools.is_tool_installed(tool_name):
                try:
                    path = tools.get_tool_path(tool_name)
                    click.echo(f"    Path: {path}")
                except ToolNotFoundError:
                    click.echo(f"    Path: Not found")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('tool', type=click.Choice(['slc-cli', 'zap']))
def versions(tool):
    """List available versions for a tool."""
    try:
        tools = SimplicityTools()
        available_versions = tools.get_available_versions(tool)
        
        if available_versions:
            click.echo(f"Available versions for {tool}:")
            for version in available_versions:
                click.echo(f"  {version}")
        else:
            click.echo(f"No versions found for {tool}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--target', default='~/bin', help='Directory to symlink binaries to (default: ~/bin)')
@click.option('--force', is_flag=True, help='Overwrite existing symlinks if they exist')
def link_binaries(target, force):
    """Symlink zap-cli and slc-cli to a directory in your PATH (default: ~/bin)."""
    tools = SimplicityTools()
    bin_dir = Path(os.path.expanduser(target))
    bin_dir.mkdir(parents=True, exist_ok=True)

    binaries = {
        'slc-cli': tools.get_slc_path(),
        'zap-cli': tools.get_tool_path('zap')
    }

    for name, src_path in binaries.items():
        dest_path = bin_dir / name
        try:
            if dest_path.exists() or dest_path.is_symlink():
                if force:
                    dest_path.unlink()
                else:
                    click.echo(f"Symlink {dest_path} already exists. Use --force to overwrite.")
                    continue
            os.symlink(src_path, dest_path)
            click.echo(f"Symlinked {src_path} -> {dest_path}")
        except Exception as e:
            click.echo(f"Failed to symlink {name}: {e}", err=True)

    click.echo(f"Done! Make sure {bin_dir} is in your $PATH.")


if __name__ == '__main__':
    main() 