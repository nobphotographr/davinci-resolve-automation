#!/usr/bin/env python3
"""
LUT Installer for DaVinci Resolve

Automatically installs LUT files to DaVinci Resolve's LUT directory
and refreshes the LUT list in the current project.

Usage:
    # Install single LUT
    python3 lut_installer.py my_lut.cube

    # Install multiple LUTs
    python3 lut_installer.py lut1.cube lut2.cube lut3.cube

    # Install all LUTs from a directory
    python3 lut_installer.py /path/to/luts/*.cube

    # Install with custom destination (optional)
    python3 lut_installer.py --dest /custom/path my_lut.cube

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import shutil
import platform
import argparse
from pathlib import Path
from typing import List, Optional

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_lut_directory() -> str:
    """
    Get platform-specific LUT directory for DaVinci Resolve.

    Returns:
        Absolute path to LUT directory

    Raises:
        RuntimeError: If platform is not supported
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        return "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
    elif system == "Windows":
        return "C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\LUT"
    elif system == "Linux":
        # Check common Linux paths
        linux_paths = [
            os.path.expanduser("~/.local/share/DaVinciResolve/LUT"),
            "/opt/resolve/LUT"
        ]
        for path in linux_paths:
            if os.path.exists(os.path.dirname(path)):
                return path
        return linux_paths[0]  # Default to user directory
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def validate_lut_file(file_path: str) -> bool:
    """
    Validate that file is a LUT file.

    Args:
        file_path: Path to file to validate

    Returns:
        True if valid LUT file, False otherwise
    """
    valid_extensions = ['.cube', '.3dl', '.lut']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in valid_extensions


def install_lut(
    source_path: str,
    dest_dir: str,
    overwrite: bool = False
) -> bool:
    """
    Install a single LUT file.

    Args:
        source_path: Source LUT file path
        dest_dir: Destination directory
        overwrite: Whether to overwrite existing files

    Returns:
        True if installation successful, False otherwise
    """
    if not os.path.isfile(source_path):
        print(f"❌ File not found: {source_path}")
        return False

    if not validate_lut_file(source_path):
        print(f"⚠️  Skipping non-LUT file: {source_path}")
        return False

    # Ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Get filename
    filename = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, filename)

    # Check if file already exists
    if os.path.exists(dest_path) and not overwrite:
        print(f"⚠️  Already exists (use --overwrite to replace): {filename}")
        return False

    try:
        # Copy file
        shutil.copy2(source_path, dest_path)
        print(f"✅ Installed: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to install {filename}: {e}")
        return False


def refresh_lut_list() -> bool:
    """
    Refresh LUT list in DaVinci Resolve.

    Returns:
        True if refresh successful, False otherwise
    """
    try:
        import DaVinciResolveScript as dvr

        resolve = dvr.scriptapp("Resolve")
        if not resolve:
            print("⚠️  Could not connect to DaVinci Resolve")
            print("   Make sure DaVinci Resolve is running")
            return False

        pm = resolve.GetProjectManager()
        if not pm:
            print("❌ Could not access Project Manager")
            return False

        project = pm.GetCurrentProject()
        if not project:
            print("⚠️  No project currently open")
            print("   LUTs installed but not refreshed in Resolve")
            print("   Open a project and run: project.RefreshLUTList()")
            return False

        # Refresh LUT list
        success = project.RefreshLUTList()
        if success:
            print("✅ LUT list refreshed in DaVinci Resolve")
            return True
        else:
            print("⚠️  RefreshLUTList() returned False")
            return False

    except ImportError:
        print("⚠️  DaVinci Resolve Python API not available")
        print("   LUTs installed but not refreshed automatically")
        print("   Restart DaVinci Resolve to see new LUTs")
        return False
    except Exception as e:
        print(f"⚠️  Error refreshing LUT list: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install LUT files to DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my_lut.cube
  %(prog)s lut1.cube lut2.cube lut3.cube
  %(prog)s /path/to/luts/*.cube
  %(prog)s --overwrite --no-refresh my_lut.cube
        """
    )

    parser.add_argument(
        'lut_files',
        nargs='+',
        help='LUT file(s) to install (.cube, .3dl, .lut)'
    )

    parser.add_argument(
        '--dest',
        type=str,
        help='Custom destination directory (default: auto-detect)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing LUT files'
    )

    parser.add_argument(
        '--no-refresh',
        action='store_true',
        help='Do not refresh LUT list in DaVinci Resolve'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve LUT Installer")
    print("=" * 70)
    print()

    # Get destination directory
    if args.dest:
        dest_dir = args.dest
        print(f"Destination: {dest_dir} (custom)")
    else:
        try:
            dest_dir = get_lut_directory()
            print(f"Destination: {dest_dir}")
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)

    print()

    # Install LUTs
    installed_count = 0
    skipped_count = 0

    for lut_file in args.lut_files:
        # Expand user home directory
        lut_file = os.path.expanduser(lut_file)

        if install_lut(lut_file, dest_dir, args.overwrite):
            installed_count += 1
        else:
            skipped_count += 1

    print()
    print("-" * 70)
    print(f"Summary: {installed_count} installed, {skipped_count} skipped")
    print("-" * 70)

    # Refresh LUT list in Resolve
    if not args.no_refresh and installed_count > 0:
        print()
        print("Refreshing LUT list in DaVinci Resolve...")
        refresh_lut_list()

    print()
    print("=" * 70)
    print("Installation complete!")
    print("=" * 70)

    if installed_count > 0:
        print()
        print("Next steps:")
        print("1. Open Color page in DaVinci Resolve")
        print("2. Select a clip")
        print("3. Right-click on a node → LUTs → Your new LUTs should appear")
        print()


if __name__ == "__main__":
    main()
