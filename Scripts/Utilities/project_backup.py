#!/usr/bin/env python3
"""
Project Backup Manager for DaVinci Resolve

Automated backup, restore, and management of DaVinci Resolve projects
with version control and retention policies.

Usage:
    # Backup current project
    python3 project_backup.py --backup

    # Backup with note
    python3 project_backup.py --backup --note "Before major changes"

    # List all backups
    python3 project_backup.py --list

    # Backup with retention policy (keep last 5)
    python3 project_backup.py --backup --keep 5

    # Clean old backups
    python3 project_backup.py --clean --keep 10

    # Restore from backup
    python3 project_backup.py --restore backup_file.drp

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_default_backup_dir() -> str:
    """
    Get default backup directory.

    Returns:
        Path to default backup directory
    """
    home = Path.home()
    backup_dir = home / "DaVinci_Resolve_Backups"
    backup_dir.mkdir(exist_ok=True)
    return str(backup_dir)


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def generate_backup_filename(project_name: str, note: Optional[str] = None) -> str:
    """
    Generate backup filename with timestamp.

    Args:
        project_name: Name of the project
        note: Optional note to include in filename

    Returns:
        Backup filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sanitize project name for filename
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')

    if note:
        # Sanitize note
        safe_note = "".join(c for c in note if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_note = safe_note.replace(' ', '_')
        return f"{safe_name}_{timestamp}_{safe_note}.drp"
    else:
        return f"{safe_name}_{timestamp}.drp"


def backup_project(
    project_manager,
    project,
    output_dir: str,
    note: Optional[str] = None
) -> Optional[str]:
    """
    Backup current project.

    Args:
        project_manager: ProjectManager object
        project: Project object
        output_dir: Output directory for backup
        note: Optional note for the backup

    Returns:
        Path to backup file if successful, None otherwise
    """
    project_name = project.GetName()
    backup_filename = generate_backup_filename(project_name, note)
    backup_path = os.path.join(output_dir, backup_filename)

    print(f"Backing up project: {project_name}")
    print(f"Output: {backup_path}")

    if note:
        print(f"Note: {note}")

    print()

    try:
        # Export project as .drp file
        success = project_manager.ExportProject(project_name, backup_path)

        if success:
            # Get file size
            file_size = os.path.getsize(backup_path)
            print(f"✅ Backup created successfully")
            print(f"   Size: {format_size(file_size)}")
            print(f"   Path: {backup_path}")
            return backup_path
        else:
            print(f"❌ Failed to create backup")
            return None

    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None


def list_backups(backup_dir: str) -> List[Dict[str, Any]]:
    """
    List all backup files in directory.

    Args:
        backup_dir: Directory containing backups

    Returns:
        List of backup info dictionaries
    """
    backup_files = []

    if not os.path.isdir(backup_dir):
        return backup_files

    for filename in os.listdir(backup_dir):
        if filename.endswith('.drp'):
            filepath = os.path.join(backup_dir, filename)

            # Get file stats
            stat = os.stat(filepath)
            file_size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime)

            # Parse filename
            parts = filename[:-4].split('_')  # Remove .drp extension

            # Try to extract note (everything after timestamp)
            note = None
            if len(parts) > 3:
                # Check if third and fourth parts look like timestamp
                if len(parts[1]) == 8 and len(parts[2]) == 6:  # YYYYMMDD_HHMMSS
                    note = '_'.join(parts[3:])

            backup_files.append({
                'filename': filename,
                'filepath': filepath,
                'size': file_size,
                'modified': mtime,
                'note': note
            })

    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: x['modified'], reverse=True)

    return backup_files


def print_backup_list(backups: List[Dict[str, Any]]):
    """
    Print formatted list of backups.

    Args:
        backups: List of backup info dictionaries
    """
    print("=" * 70)
    print("Available Backups")
    print("=" * 70)
    print()

    if not backups:
        print("No backups found")
        print()
        return

    for i, backup in enumerate(backups, 1):
        print(f"{i}. {backup['filename']}")
        print(f"   Date: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Size: {format_size(backup['size'])}")

        if backup['note']:
            print(f"   Note: {backup['note']}")

        print()

    print("=" * 70)


def clean_old_backups(backup_dir: str, keep_count: int, dry_run: bool = False) -> int:
    """
    Remove old backups, keeping only specified number.

    Args:
        backup_dir: Directory containing backups
        keep_count: Number of backups to keep
        dry_run: If True, only show what would be deleted

    Returns:
        Number of backups removed
    """
    backups = list_backups(backup_dir)

    if len(backups) <= keep_count:
        print(f"Found {len(backups)} backup(s), keeping all (limit: {keep_count})")
        return 0

    to_remove = backups[keep_count:]

    print(f"Found {len(backups)} backup(s), removing {len(to_remove)} old backup(s)")
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be deleted")
        print()

    removed_count = 0

    for backup in to_remove:
        if dry_run:
            print(f"  Would remove: {backup['filename']}")
            removed_count += 1
        else:
            try:
                os.remove(backup['filepath'])
                print(f"  ✅ Removed: {backup['filename']}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {backup['filename']}: {e}")

    return removed_count


def restore_project(
    project_manager,
    backup_path: str,
    new_project_name: Optional[str] = None
) -> bool:
    """
    Restore project from backup.

    Args:
        project_manager: ProjectManager object
        backup_path: Path to backup file
        new_project_name: Optional new name for restored project

    Returns:
        True if successful
    """
    if not os.path.isfile(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False

    # Get original project name from filename
    filename = os.path.basename(backup_path)
    original_name = filename[:-4]  # Remove .drp

    # Use new name if provided, otherwise use original with timestamp
    if new_project_name:
        import_name = new_project_name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import_name = f"{original_name}_restored_{timestamp}"

    print(f"Restoring project from: {filename}")
    print(f"New project name: {import_name}")
    print()

    try:
        success = project_manager.ImportProject(backup_path, import_name)

        if success:
            print(f"✅ Project restored successfully")
            print(f"   Project name: {import_name}")
            print()
            print("⚠️  Note: Restored project is not automatically opened")
            print("   Please open it manually from the project list")
            return True
        else:
            print(f"❌ Failed to restore project")
            return False

    except Exception as e:
        print(f"❌ Error restoring project: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Backup and restore DaVinci Resolve projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup current project
  %(prog)s --backup

  # Backup with note
  %(prog)s --backup --note "Before color grading"

  # Backup to custom directory
  %(prog)s --backup --output ~/MyBackups/

  # Backup with retention (keep last 5)
  %(prog)s --backup --keep 5

  # List all backups
  %(prog)s --list

  # Clean old backups (keep last 10)
  %(prog)s --clean --keep 10

  # Clean with dry run
  %(prog)s --clean --keep 10 --dry-run

  # Restore from backup
  %(prog)s --restore MyProject_20250130_143022.drp

  # Restore with new name
  %(prog)s --restore backup.drp --name "Restored_Project"
        """
    )

    # Actions
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Backup current project'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all backups'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove old backups'
    )

    parser.add_argument(
        '--restore',
        type=str,
        metavar='FILE',
        help='Restore project from backup file'
    )

    # Options
    parser.add_argument(
        '--output',
        type=str,
        metavar='DIR',
        help='Backup directory (default: ~/DaVinci_Resolve_Backups)'
    )

    parser.add_argument(
        '--note',
        type=str,
        metavar='TEXT',
        help='Note to include in backup filename'
    )

    parser.add_argument(
        '--keep',
        type=int,
        metavar='N',
        help='Number of backups to keep (use with --backup or --clean)'
    )

    parser.add_argument(
        '--name',
        type=str,
        metavar='NAME',
        help='New project name (use with --restore)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Need at least one action
    if not any([args.backup, args.list, args.clean, args.restore]):
        parser.print_help()
        return

    # Get backup directory
    backup_dir = args.output or get_default_backup_dir()

    print("=" * 70)
    print("DaVinci Resolve Project Backup Manager")
    print("=" * 70)
    print()
    print(f"Backup Directory: {backup_dir}")
    print()

    # List backups (no connection needed)
    if args.list:
        backups = list_backups(backup_dir)
        print_backup_list(backups)
        return

    # Clean backups (no connection needed)
    if args.clean:
        if not args.keep:
            print("❌ --keep is required when using --clean")
            sys.exit(1)

        print("=" * 70)
        print("Cleaning Old Backups")
        print("=" * 70)
        print()

        removed = clean_old_backups(backup_dir, args.keep, dry_run=args.dry_run)

        print()
        print("=" * 70)

        if args.dry_run:
            print(f"Would remove {removed} backup(s)")
        else:
            print(f"✅ Removed {removed} backup(s)")

        print("=" * 70)
        return

    # For backup and restore, need connection
    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")

        if not resolve:
            print("❌ Could not connect to DaVinci Resolve")
            print("   Make sure DaVinci Resolve is running")
            sys.exit(1)

        pm = resolve.GetProjectManager()

        if not pm:
            print("❌ Could not access Project Manager")
            sys.exit(1)

        print("✅ Connected to DaVinci Resolve")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Backup current project
    if args.backup:
        project = pm.GetCurrentProject()

        if not project:
            print("❌ No project is currently open")
            print("   Please open a project to backup")
            sys.exit(1)

        print("=" * 70)
        print("Creating Backup")
        print("=" * 70)
        print()

        backup_path = backup_project(pm, project, backup_dir, note=args.note)

        if backup_path and args.keep:
            print()
            print("Applying retention policy...")
            print()
            removed = clean_old_backups(backup_dir, args.keep)

            if removed > 0:
                print()
                print(f"✅ Removed {removed} old backup(s)")

        print()
        print("=" * 70)

    # Restore project
    if args.restore:
        # Check if path is relative or absolute
        if os.path.isabs(args.restore):
            restore_path = args.restore
        else:
            # Try backup directory first
            restore_path = os.path.join(backup_dir, args.restore)

            # If not found, try current directory
            if not os.path.isfile(restore_path):
                restore_path = args.restore

        print("=" * 70)
        print("Restoring Project")
        print("=" * 70)
        print()

        restore_project(pm, restore_path, new_project_name=args.name)

        print()
        print("=" * 70)


if __name__ == "__main__":
    main()
