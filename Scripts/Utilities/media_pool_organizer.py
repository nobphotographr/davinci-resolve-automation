#!/usr/bin/env python3
"""
Media Pool Organizer for DaVinci Resolve

Organize, analyze, and manage media pool structure with automatic
classification, statistics, and cleanup tools.

Usage:
    # Show media pool statistics
    python3 media_pool_organizer.py --stats

    # Display bin structure as tree
    python3 media_pool_organizer.py --tree

    # Organize clips by resolution
    python3 media_pool_organizer.py --organize-by resolution

    # Organize clips by codec
    python3 media_pool_organizer.py --organize-by codec

    # Search for clips
    python3 media_pool_organizer.py --search "interview"

    # Clean up empty bins
    python3 media_pool_organizer.py --clean-empty-bins

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_or_create_bin(parent_folder, bin_name: str):
    """
    Get existing bin or create new one.

    Args:
        parent_folder: Parent folder object
        bin_name: Name of bin to get or create

    Returns:
        Folder object
    """
    # Get existing subfolders
    subfolders = parent_folder.GetSubFolderList()

    if subfolders:
        for subfolder in subfolders:
            if subfolder.GetName() == bin_name:
                return subfolder

    # Create new bin if not found
    return parent_folder.AddSubFolder(bin_name)


def get_all_clips_recursive(folder, clips_list: Optional[List] = None) -> List:
    """
    Recursively get all clips from folder and subfolders.

    Args:
        folder: Folder object to search
        clips_list: List to accumulate clips (internal use)

    Returns:
        List of all MediaPoolItem objects
    """
    if clips_list is None:
        clips_list = []

    # Get clips in current folder
    clips = folder.GetClipList()
    if clips:
        clips_list.extend(clips)

    # Recurse into subfolders
    subfolders = folder.GetSubFolderList()
    if subfolders:
        for subfolder in subfolders:
            get_all_clips_recursive(subfolder, clips_list)

    return clips_list


def get_folder_tree(folder, prefix: str = "", is_last: bool = True) -> List[str]:
    """
    Get folder structure as tree diagram.

    Args:
        folder: Folder object
        prefix: Prefix for tree lines (internal use)
        is_last: Whether this is the last item (internal use)

    Returns:
        List of formatted tree lines
    """
    lines = []

    # Current folder line
    connector = "└── " if is_last else "├── "
    folder_name = folder.GetName()

    # Count clips in this folder
    clips = folder.GetClipList()
    clip_count = len(clips) if clips else 0

    lines.append(f"{prefix}{connector}📁 {folder_name} ({clip_count} clips)")

    # Prepare prefix for children
    extension = "    " if is_last else "│   "
    new_prefix = prefix + extension

    # Get subfolders
    subfolders = folder.GetSubFolderList()

    if subfolders:
        for i, subfolder in enumerate(subfolders):
            is_last_subfolder = (i == len(subfolders) - 1)
            lines.extend(get_folder_tree(subfolder, new_prefix, is_last_subfolder))

    return lines


def get_clip_metadata(clip) -> Dict[str, Any]:
    """
    Extract metadata from clip.

    Args:
        clip: MediaPoolItem object

    Returns:
        Dictionary with clip metadata
    """
    metadata = {
        'name': clip.GetName(),
        'resolution': None,
        'fps': None,
        'codec': None,
        'duration': None,
        'file_path': None
    }

    try:
        # Get clip properties
        props = clip.GetClipProperty()

        if props:
            # Resolution
            width = props.get('Width', props.get('Resolution Width'))
            height = props.get('Height', props.get('Resolution Height'))
            if width and height:
                metadata['resolution'] = f"{width}x{height}"

            # Frame rate
            fps = props.get('FPS', props.get('Frame Rate'))
            if fps:
                metadata['fps'] = str(fps)

            # Codec
            codec = props.get('Video Codec', props.get('Codec'))
            if codec:
                metadata['codec'] = codec

            # Duration
            duration = props.get('Duration', props.get('Frames'))
            if duration:
                metadata['duration'] = duration

            # File path
            file_path = props.get('File Path', props.get('File Name'))
            if file_path:
                metadata['file_path'] = file_path

    except Exception as e:
        print(f"⚠️  Could not read metadata for {metadata['name']}: {e}")

    return metadata


def calculate_media_pool_stats(media_pool) -> Dict[str, Any]:
    """
    Calculate comprehensive media pool statistics.

    Args:
        media_pool: MediaPool object

    Returns:
        Dictionary with statistics
    """
    root_folder = media_pool.GetRootFolder()
    all_clips = get_all_clips_recursive(root_folder)

    stats = {
        'total_clips': len(all_clips),
        'by_resolution': defaultdict(int),
        'by_codec': defaultdict(int),
        'by_fps': defaultdict(int),
        'folder_count': 0,
        'empty_folders': []
    }

    # Analyze clips
    for clip in all_clips:
        metadata = get_clip_metadata(clip)

        if metadata['resolution']:
            stats['by_resolution'][metadata['resolution']] += 1

        if metadata['codec']:
            stats['by_codec'][metadata['codec']] += 1

        if metadata['fps']:
            stats['by_fps'][metadata['fps']] += 1

    # Count folders recursively
    def count_folders(folder):
        count = 1  # Count current folder
        clips = folder.GetClipList()
        clip_count = len(clips) if clips else 0

        if clip_count == 0:
            stats['empty_folders'].append(folder.GetName())

        subfolders = folder.GetSubFolderList()
        if subfolders:
            for subfolder in subfolders:
                count += count_folders(subfolder)

        return count

    stats['folder_count'] = count_folders(root_folder)

    return stats


def print_stats(stats: Dict[str, Any]):
    """
    Print media pool statistics.

    Args:
        stats: Statistics dictionary
    """
    print("=" * 70)
    print("Media Pool Statistics")
    print("=" * 70)
    print()

    print(f"Total Clips: {stats['total_clips']}")
    print(f"Total Bins: {stats['folder_count']}")
    print(f"Empty Bins: {len(stats['empty_folders'])}")
    print()

    if stats['by_resolution']:
        print("-" * 70)
        print("Clips by Resolution")
        print("-" * 70)
        for resolution, count in sorted(stats['by_resolution'].items()):
            print(f"  {resolution}: {count} clips")
        print()

    if stats['by_codec']:
        print("-" * 70)
        print("Clips by Codec")
        print("-" * 70)
        for codec, count in sorted(stats['by_codec'].items()):
            print(f"  {codec}: {count} clips")
        print()

    if stats['by_fps']:
        print("-" * 70)
        print("Clips by Frame Rate")
        print("-" * 70)
        for fps, count in sorted(stats['by_fps'].items()):
            print(f"  {fps} fps: {count} clips")
        print()

    if stats['empty_folders']:
        print("-" * 70)
        print("Empty Bins")
        print("-" * 70)
        for folder_name in stats['empty_folders']:
            print(f"  📁 {folder_name}")
        print()

    print("=" * 70)


def print_tree(media_pool):
    """
    Print media pool structure as tree.

    Args:
        media_pool: MediaPool object
    """
    print("=" * 70)
    print("Media Pool Structure")
    print("=" * 70)
    print()

    root_folder = media_pool.GetRootFolder()
    tree_lines = get_folder_tree(root_folder, "", True)

    for line in tree_lines:
        print(line)

    print()
    print("=" * 70)


def organize_by_resolution(media_pool, dry_run: bool = False) -> int:
    """
    Organize clips by resolution into separate bins.

    Args:
        media_pool: MediaPool object
        dry_run: If True, only print what would be done

    Returns:
        Number of clips organized
    """
    root_folder = media_pool.GetRootFolder()
    all_clips = get_all_clips_recursive(root_folder)

    # Group clips by resolution
    clips_by_resolution = defaultdict(list)

    for clip in all_clips:
        metadata = get_clip_metadata(clip)
        resolution = metadata['resolution'] or 'Unknown'
        clips_by_resolution[resolution].append(clip)

    if dry_run:
        print("Dry run - would organize clips as follows:")
        print()

    moved_count = 0

    for resolution, clips in sorted(clips_by_resolution.items()):
        print(f"📁 {resolution}: {len(clips)} clips")

        if not dry_run:
            # Create or get bin
            target_bin = get_or_create_bin(root_folder, resolution)

            # Move clips
            for clip in clips:
                try:
                    if media_pool.MoveClips([clip], target_bin):
                        moved_count += 1
                        print(f"  ✅ Moved: {clip.GetName()}")
                    else:
                        print(f"  ⚠️  Could not move: {clip.GetName()}")
                except Exception as e:
                    print(f"  ❌ Error moving {clip.GetName()}: {e}")
        print()

    return moved_count


def organize_by_codec(media_pool, dry_run: bool = False) -> int:
    """
    Organize clips by codec into separate bins.

    Args:
        media_pool: MediaPool object
        dry_run: If True, only print what would be done

    Returns:
        Number of clips organized
    """
    root_folder = media_pool.GetRootFolder()
    all_clips = get_all_clips_recursive(root_folder)

    # Group clips by codec
    clips_by_codec = defaultdict(list)

    for clip in all_clips:
        metadata = get_clip_metadata(clip)
        codec = metadata['codec'] or 'Unknown'
        clips_by_codec[codec].append(clip)

    if dry_run:
        print("Dry run - would organize clips as follows:")
        print()

    moved_count = 0

    for codec, clips in sorted(clips_by_codec.items()):
        print(f"📁 {codec}: {len(clips)} clips")

        if not dry_run:
            # Create or get bin
            target_bin = get_or_create_bin(root_folder, codec)

            # Move clips
            for clip in clips:
                try:
                    if media_pool.MoveClips([clip], target_bin):
                        moved_count += 1
                        print(f"  ✅ Moved: {clip.GetName()}")
                    else:
                        print(f"  ⚠️  Could not move: {clip.GetName()}")
                except Exception as e:
                    print(f"  ❌ Error moving {clip.GetName()}: {e}")
        print()

    return moved_count


def search_clips(media_pool, query: str) -> List[Tuple[Any, str]]:
    """
    Search for clips by name.

    Args:
        media_pool: MediaPool object
        query: Search query

    Returns:
        List of (clip, folder_path) tuples
    """
    root_folder = media_pool.GetRootFolder()
    results = []

    def search_in_folder(folder, path: str = ""):
        """Recursive search helper."""
        folder_name = folder.GetName()
        current_path = f"{path}/{folder_name}" if path else folder_name

        # Search in current folder
        clips = folder.GetClipList()
        if clips:
            for clip in clips:
                if query.lower() in clip.GetName().lower():
                    results.append((clip, current_path))

        # Search in subfolders
        subfolders = folder.GetSubFolderList()
        if subfolders:
            for subfolder in subfolders:
                search_in_folder(subfolder, current_path)

    search_in_folder(root_folder)
    return results


def clean_empty_bins(media_pool, dry_run: bool = False) -> int:
    """
    Remove empty bins from media pool.

    Args:
        media_pool: MediaPool object
        dry_run: If True, only print what would be done

    Returns:
        Number of bins removed
    """
    root_folder = media_pool.GetRootFolder()
    removed_count = 0

    def remove_empty_recursive(folder):
        """Recursive empty bin removal."""
        nonlocal removed_count

        subfolders = folder.GetSubFolderList()
        if not subfolders:
            return

        # Process each subfolder
        for subfolder in list(subfolders):  # Convert to list to avoid modification during iteration
            # Recurse first
            remove_empty_recursive(subfolder)

            # Check if empty (no clips and no subfolders)
            clips = subfolder.GetClipList()
            remaining_subfolders = subfolder.GetSubFolderList()

            is_empty = (not clips or len(clips) == 0) and (not remaining_subfolders or len(remaining_subfolders) == 0)

            if is_empty:
                folder_name = subfolder.GetName()

                if dry_run:
                    print(f"  Would remove: 📁 {folder_name}")
                    removed_count += 1
                else:
                    # Try to delete the subfolder
                    media_pool.SetCurrentFolder(folder)
                    if media_pool.DeleteSubFolders([subfolder]):
                        print(f"  ✅ Removed: 📁 {folder_name}")
                        removed_count += 1
                    else:
                        print(f"  ⚠️  Could not remove: 📁 {folder_name}")

    remove_empty_recursive(root_folder)
    return removed_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Organize and manage DaVinci Resolve media pool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show media pool statistics
  %(prog)s --stats

  # Display bin structure
  %(prog)s --tree

  # Organize by resolution
  %(prog)s --organize-by resolution

  # Organize by codec
  %(prog)s --organize-by codec

  # Search for clips
  %(prog)s --search "interview"

  # Clean empty bins (dry run)
  %(prog)s --clean-empty-bins --dry-run

  # Clean empty bins (actual)
  %(prog)s --clean-empty-bins
        """
    )

    # Actions
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show media pool statistics'
    )

    parser.add_argument(
        '--tree',
        action='store_true',
        help='Display media pool structure as tree'
    )

    parser.add_argument(
        '--organize-by',
        type=str,
        choices=['resolution', 'codec'],
        metavar='TYPE',
        help='Organize clips by resolution or codec'
    )

    parser.add_argument(
        '--search',
        type=str,
        metavar='QUERY',
        help='Search for clips by name'
    )

    parser.add_argument(
        '--clean-empty-bins',
        action='store_true',
        help='Remove empty bins from media pool'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Need at least one action
    if not any([args.stats, args.tree, args.organize_by, args.search, args.clean_empty_bins]):
        parser.print_help()
        return

    print("=" * 70)
    print("DaVinci Resolve Media Pool Organizer")
    print("=" * 70)
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

    # Execute actions
    if args.stats:
        stats = calculate_media_pool_stats(media_pool)
        print_stats(stats)

    if args.tree:
        print_tree(media_pool)

    if args.organize_by:
        print("=" * 70)
        print(f"Organizing by {args.organize_by.capitalize()}")
        print("=" * 70)
        print()

        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print()

        if args.organize_by == 'resolution':
            moved = organize_by_resolution(media_pool, dry_run=args.dry_run)
        elif args.organize_by == 'codec':
            moved = organize_by_codec(media_pool, dry_run=args.dry_run)

        if not args.dry_run:
            print("=" * 70)
            print(f"✅ Organized {moved} clips")
            print("=" * 70)

    if args.search:
        print("=" * 70)
        print(f"Searching for: {args.search}")
        print("=" * 70)
        print()

        results = search_clips(media_pool, args.search)

        if results:
            print(f"Found {len(results)} clip(s):")
            print()
            for clip, path in results:
                print(f"🎬 {clip.GetName()}")
                print(f"   Location: {path}")
                print()
        else:
            print("No clips found matching query")
            print()

        print("=" * 70)

    if args.clean_empty_bins:
        print("=" * 70)
        print("Cleaning Empty Bins")
        print("=" * 70)
        print()

        if args.dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            print()

        removed = clean_empty_bins(media_pool, dry_run=args.dry_run)

        print()
        print("=" * 70)

        if args.dry_run:
            print(f"Would remove {removed} empty bin(s)")
        else:
            print(f"✅ Removed {removed} empty bin(s)")

        print("=" * 70)


if __name__ == "__main__":
    main()
