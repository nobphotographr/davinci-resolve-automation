#!/usr/bin/env python3
"""
Batch Clip Renamer for DaVinci Resolve

Batch rename clips in media pool with regex patterns, sequential numbering,
metadata-based naming, and prefix/suffix operations.

Usage:
    # Add prefix to all clips
    python3 batch_clip_renamer.py --prefix "FOOTAGE_"

    # Add suffix to all clips
    python3 batch_clip_renamer.py --suffix "_v1"

    # Replace text using regex
    python3 batch_clip_renamer.py --replace "old_pattern" "new_pattern"

    # Sequential numbering
    python3 batch_clip_renamer.py --sequential --start 1 --digits 3

    # Rename from metadata
    python3 batch_clip_renamer.py --from-metadata "Scene_{Scene}_Shot_{Shot}"

    # Dry run to preview
    python3 batch_clip_renamer.py --prefix "TEST_" --dry-run

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import re
from typing import List, Dict, Optional, Any, Tuple

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_all_clips_from_pool(media_pool) -> List[Tuple[Any, str]]:
    """
    Get all clips from media pool recursively.

    Args:
        media_pool: MediaPool object

    Returns:
        List of (clip, folder_path) tuples
    """
    clips = []

    def traverse_folder(folder, path: str = ""):
        """Recursive traversal helper."""
        folder_name = folder.GetName()
        current_path = f"{path}/{folder_name}" if path else folder_name

        # Get clips in current folder
        folder_clips = folder.GetClipList()
        if folder_clips:
            for clip in folder_clips:
                clips.append((clip, current_path))

        # Recurse into subfolders
        subfolders = folder.GetSubFolderList()
        if subfolders:
            for subfolder in subfolders:
                traverse_folder(subfolder, current_path)

    root_folder = media_pool.GetRootFolder()
    traverse_folder(root_folder)

    return clips


def add_prefix(clips: List[Tuple[Any, str]], prefix: str, dry_run: bool = False) -> int:
    """
    Add prefix to clip names.

    Args:
        clips: List of (clip, path) tuples
        prefix: Prefix to add
        dry_run: If True, don't actually rename

    Returns:
        Number of clips renamed
    """
    renamed = 0

    for clip, path in clips:
        old_name = clip.GetName()
        new_name = f"{prefix}{old_name}"

        if dry_run:
            print(f"  Would rename: {old_name} → {new_name}")
            renamed += 1
        else:
            success = clip.SetClipProperty("Clip Name", new_name)
            if success:
                print(f"  ✅ Renamed: {old_name} → {new_name}")
                renamed += 1
            else:
                print(f"  ❌ Failed: {old_name}")

    return renamed


def add_suffix(clips: List[Tuple[Any, str]], suffix: str, dry_run: bool = False) -> int:
    """
    Add suffix to clip names (before extension).

    Args:
        clips: List of (clip, path) tuples
        suffix: Suffix to add
        dry_run: If True, don't actually rename

    Returns:
        Number of clips renamed
    """
    renamed = 0

    for clip, path in clips:
        old_name = clip.GetName()

        # Split name and extension
        if '.' in old_name:
            name_parts = old_name.rsplit('.', 1)
            new_name = f"{name_parts[0]}{suffix}.{name_parts[1]}"
        else:
            new_name = f"{old_name}{suffix}"

        if dry_run:
            print(f"  Would rename: {old_name} → {new_name}")
            renamed += 1
        else:
            success = clip.SetClipProperty("Clip Name", new_name)
            if success:
                print(f"  ✅ Renamed: {old_name} → {new_name}")
                renamed += 1
            else:
                print(f"  ❌ Failed: {old_name}")

    return renamed


def replace_pattern(
    clips: List[Tuple[Any, str]],
    pattern: str,
    replacement: str,
    dry_run: bool = False
) -> int:
    """
    Replace text using regex pattern.

    Args:
        clips: List of (clip, path) tuples
        pattern: Regex pattern to find
        replacement: Replacement text
        dry_run: If True, don't actually rename

    Returns:
        Number of clips renamed
    """
    try:
        regex = re.compile(pattern)
    except Exception as e:
        print(f"❌ Invalid regex pattern: {e}")
        return 0

    renamed = 0

    for clip, path in clips:
        old_name = clip.GetName()
        new_name = regex.sub(replacement, old_name)

        # Skip if name didn't change
        if new_name == old_name:
            continue

        if dry_run:
            print(f"  Would rename: {old_name} → {new_name}")
            renamed += 1
        else:
            success = clip.SetClipProperty("Clip Name", new_name)
            if success:
                print(f"  ✅ Renamed: {old_name} → {new_name}")
                renamed += 1
            else:
                print(f"  ❌ Failed: {old_name}")

    return renamed


def sequential_rename(
    clips: List[Tuple[Any, str]],
    template: str,
    start: int,
    digits: int,
    dry_run: bool = False
) -> int:
    """
    Rename clips with sequential numbering.

    Args:
        clips: List of (clip, path) tuples
        template: Template with {n} placeholder
        start: Starting number
        digits: Number of digits (zero-padded)
        dry_run: If True, don't actually rename

    Returns:
        Number of clips renamed
    """
    renamed = 0

    for i, (clip, path) in enumerate(clips):
        old_name = clip.GetName()
        number = start + i
        padded_number = str(number).zfill(digits)

        # Replace {n} placeholder
        new_name = template.replace("{n}", padded_number)

        if dry_run:
            print(f"  Would rename: {old_name} → {new_name}")
            renamed += 1
        else:
            success = clip.SetClipProperty("Clip Name", new_name)
            if success:
                print(f"  ✅ Renamed: {old_name} → {new_name}")
                renamed += 1
            else:
                print(f"  ❌ Failed: {old_name}")

    return renamed


def rename_from_metadata(
    clips: List[Tuple[Any, str]],
    template: str,
    dry_run: bool = False
) -> int:
    """
    Rename clips using metadata template.

    Args:
        clips: List of (clip, path) tuples
        template: Template with {FieldName} placeholders
        dry_run: If True, don't actually rename

    Returns:
        Number of clips renamed
    """
    renamed = 0

    # Extract field names from template
    field_pattern = re.compile(r'\{(\w+)\}')
    fields = field_pattern.findall(template)

    if not fields:
        print("❌ Template must contain at least one {FieldName} placeholder")
        return 0

    for clip, path in clips:
        old_name = clip.GetName()
        new_name = template

        # Replace each field placeholder with metadata value
        skip_clip = False
        for field in fields:
            try:
                value = clip.GetMetadata(field)
                if value and value != "":
                    new_name = new_name.replace(f"{{{field}}}", value)
                else:
                    # Skip clips without required metadata
                    skip_clip = True
                    break
            except:
                skip_clip = True
                break

        if skip_clip:
            print(f"  ⚠️  Skipped (missing metadata): {old_name}")
            continue

        if dry_run:
            print(f"  Would rename: {old_name} → {new_name}")
            renamed += 1
        else:
            success = clip.SetClipProperty("Clip Name", new_name)
            if success:
                print(f"  ✅ Renamed: {old_name} → {new_name}")
                renamed += 1
            else:
                print(f"  ❌ Failed: {old_name}")

    return renamed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch rename clips in DaVinci Resolve media pool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add prefix
  %(prog)s --prefix "FOOTAGE_"

  # Add suffix (before extension)
  %(prog)s --suffix "_v1"

  # Replace text
  %(prog)s --replace "old" "new"

  # Replace with regex
  %(prog)s --replace "Scene(\\d+)" "S\\1"

  # Sequential numbering
  %(prog)s --sequential "Clip_{n}" --start 1 --digits 3

  # Rename from metadata
  %(prog)s --from-metadata "Scene_{Scene}_Shot_{Shot}"

  # Dry run
  %(prog)s --prefix "TEST_" --dry-run
        """
    )

    # Rename operations (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group(required=True)

    operation_group.add_argument(
        '--prefix',
        type=str,
        metavar='TEXT',
        help='Add prefix to clip names'
    )

    operation_group.add_argument(
        '--suffix',
        type=str,
        metavar='TEXT',
        help='Add suffix to clip names (before extension)'
    )

    operation_group.add_argument(
        '--replace',
        nargs=2,
        metavar=('PATTERN', 'REPLACEMENT'),
        help='Replace text using regex pattern'
    )

    operation_group.add_argument(
        '--sequential',
        type=str,
        metavar='TEMPLATE',
        help='Sequential numbering (use {n} for number)'
    )

    operation_group.add_argument(
        '--from-metadata',
        type=str,
        metavar='TEMPLATE',
        help='Rename using metadata template (e.g., "Scene_{Scene}_Shot_{Shot}")'
    )

    # Sequential numbering options
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        metavar='N',
        help='Starting number for sequential rename (default: 1)'
    )

    parser.add_argument(
        '--digits',
        type=int,
        default=3,
        metavar='N',
        help='Number of digits for sequential rename (default: 3)'
    )

    # Other options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without renaming'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve Batch Clip Renamer")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No clips will be renamed")
        print()

    # Connect to DaVinci Resolve
    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")

        if not resolve:
            print("❌ Could not connect to DaVinci Resolve")
            print("   Make sure DaVinci Resolve is running")
            sys.exit(1)

        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject()

        if not project:
            print("❌ No project is currently open")
            print("   Please open a project in DaVinci Resolve")
            sys.exit(1)

        media_pool = project.GetMediaPool()

        if not media_pool:
            print("❌ Could not access media pool")
            sys.exit(1)

        print(f"✅ Connected to project: {project.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Get all clips
    print("Scanning media pool...")
    clips = get_all_clips_from_pool(media_pool)
    print(f"Found {len(clips)} clip(s)")
    print()

    if not clips:
        print("No clips found in media pool")
        sys.exit(0)

    # Execute rename operation
    print("Renaming clips...")
    print()

    renamed = 0

    if args.prefix:
        renamed = add_prefix(clips, args.prefix, dry_run=args.dry_run)

    elif args.suffix:
        renamed = add_suffix(clips, args.suffix, dry_run=args.dry_run)

    elif args.replace:
        pattern, replacement = args.replace
        renamed = replace_pattern(clips, pattern, replacement, dry_run=args.dry_run)

    elif args.sequential:
        renamed = sequential_rename(
            clips,
            args.sequential,
            args.start,
            args.digits,
            dry_run=args.dry_run
        )

    elif args.from_metadata:
        renamed = rename_from_metadata(clips, args.from_metadata, dry_run=args.dry_run)

    # Print summary
    print()
    print("=" * 70)

    if args.dry_run:
        print(f"Would rename {renamed} clip(s)")
    else:
        print(f"✅ Renamed {renamed} clip(s)")

    print("=" * 70)


if __name__ == "__main__":
    main()
