#!/usr/bin/env python3
"""
Clip Color Manager for DaVinci Resolve

Manage, analyze, and bulk-modify clip colors in timeline and media pool.

Usage:
    # Show color distribution
    python3 clip_color_manager.py --stats

    # List clips by color
    python3 clip_color_manager.py --list --color Orange

    # Set color on clips matching search
    python3 clip_color_manager.py --set-color Blue --search "interview"

    # Clear color from all clips
    python3 clip_color_manager.py --clear-color --color Orange

    # Work with timeline
    python3 clip_color_manager.py --timeline --stats

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Available clip colors in DaVinci Resolve
CLIP_COLORS = [
    'Orange', 'Apricot', 'Yellow', 'Lime', 'Olive',
    'Green', 'Teal', 'Navy', 'Blue', 'Purple',
    'Violet', 'Pink', 'Tan', 'Beige', 'Brown',
    'Chocolate'
]


def get_all_clips_from_media_pool(media_pool) -> List[Tuple[Any, str]]:
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


def get_clips_from_timeline(timeline) -> List[Any]:
    """
    Get all clips from timeline.

    Args:
        timeline: Timeline object

    Returns:
        List of TimelineItem objects
    """
    clips = []
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            clips.extend(items)

    return clips


def get_color_statistics(clips: List) -> Dict[str, int]:
    """
    Calculate color distribution.

    Args:
        clips: List of clips or (clip, path) tuples

    Returns:
        Dictionary with color counts
    """
    color_counts = defaultdict(int)

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, _ = item
        else:
            clip = item

        color = clip.GetClipColor()
        if color and color != "":
            color_counts[color] += 1
        else:
            color_counts['None'] += 1

    return dict(color_counts)


def print_color_statistics(color_counts: Dict[str, int], total_clips: int):
    """
    Print color distribution statistics.

    Args:
        color_counts: Dictionary with color counts
        total_clips: Total number of clips
    """
    print("=" * 70)
    print("Clip Color Statistics")
    print("=" * 70)
    print()

    print(f"Total Clips: {total_clips}")
    print()

    if not color_counts:
        print("No clips found")
        return

    print("-" * 70)
    print("Color Distribution")
    print("-" * 70)

    # Sort by count (descending)
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

    for color, count in sorted_colors:
        percentage = (count / total_clips) * 100
        bar_length = int(percentage / 2)  # Scale to fit in 50 chars
        bar = "█" * bar_length

        color_display = color if color else "(No Color)"
        print(f"{color_display:15} {count:4} {bar} {percentage:.1f}%")

    print()
    print("=" * 70)


def list_clips_by_color(clips: List, target_color: str):
    """
    List all clips with specific color.

    Args:
        clips: List of clips or (clip, path) tuples
        target_color: Color to filter by
    """
    print("=" * 70)
    print(f"Clips with Color: {target_color}")
    print("=" * 70)
    print()

    matching_clips = []

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item
            path = None

        color = clip.GetClipColor()

        if target_color.lower() == 'none':
            # Match clips with no color
            if not color or color == "":
                matching_clips.append((clip, path))
        else:
            # Match specific color
            if color and color.lower() == target_color.lower():
                matching_clips.append((clip, path))

    if not matching_clips:
        print(f"No clips found with color: {target_color}")
        print()
        return

    print(f"Found {len(matching_clips)} clip(s):")
    print()

    for i, (clip, path) in enumerate(matching_clips, 1):
        print(f"{i}. {clip.GetName()}")
        if path:
            print(f"   Location: {path}")
        print()

    print("=" * 70)


def set_clip_color(clips: List, color: str, search_query: Optional[str] = None, dry_run: bool = False) -> int:
    """
    Set color on clips.

    Args:
        clips: List of clips or (clip, path) tuples
        color: Color to set
        search_query: Optional search query to filter clips
        dry_run: If True, only show what would be done

    Returns:
        Number of clips updated
    """
    # Filter by search query if provided
    target_clips = []

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item
            path = None

        # Apply search filter
        if search_query:
            if search_query.lower() not in clip.GetName().lower():
                continue

        target_clips.append((clip, path))

    if not target_clips:
        print("No clips found matching criteria")
        return 0

    print(f"Setting color '{color}' on {len(target_clips)} clip(s)")
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    updated_count = 0

    for clip, path in target_clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would set color on: {clip_name}")
            updated_count += 1
        else:
            success = clip.SetClipColor(color)
            if success:
                print(f"  ✅ Set color: {clip_name}")
                updated_count += 1
            else:
                print(f"  ❌ Failed: {clip_name}")

    return updated_count


def clear_clip_color(clips: List, target_color: Optional[str] = None, dry_run: bool = False) -> int:
    """
    Clear color from clips.

    Args:
        clips: List of clips or (clip, path) tuples
        target_color: Optional specific color to clear (None = clear all)
        dry_run: If True, only show what would be done

    Returns:
        Number of clips updated
    """
    target_clips = []

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item
            path = None

        current_color = clip.GetClipColor()

        # Skip clips that already have no color
        if not current_color or current_color == "":
            continue

        # If target_color specified, only clear that color
        if target_color:
            if current_color.lower() == target_color.lower():
                target_clips.append((clip, path, current_color))
        else:
            target_clips.append((clip, path, current_color))

    if not target_clips:
        if target_color:
            print(f"No clips found with color: {target_color}")
        else:
            print("No clips with colors found")
        return 0

    if target_color:
        print(f"Clearing color '{target_color}' from {len(target_clips)} clip(s)")
    else:
        print(f"Clearing all colors from {len(target_clips)} clip(s)")
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    cleared_count = 0

    for clip, path, current_color in target_clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would clear {current_color} from: {clip_name}")
            cleared_count += 1
        else:
            success = clip.ClearClipColor()
            if success:
                print(f"  ✅ Cleared {current_color}: {clip_name}")
                cleared_count += 1
            else:
                print(f"  ❌ Failed: {clip_name}")

    return cleared_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage clip colors in DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show color distribution
  %(prog)s --stats

  # List clips with Orange color
  %(prog)s --list --color Orange

  # Set Blue color on clips with "interview" in name
  %(prog)s --set-color Blue --search "interview"

  # Clear Orange color from all clips
  %(prog)s --clear-color --color Orange

  # Clear all colors (dry-run)
  %(prog)s --clear-color --dry-run

  # Work with timeline
  %(prog)s --timeline --stats
  %(prog)s --timeline --set-color Purple --search "b-roll"

Available colors:
  Orange, Apricot, Yellow, Lime, Olive, Green, Teal, Navy,
  Blue, Purple, Violet, Pink, Tan, Beige, Brown, Chocolate
        """
    )

    # Source selection
    parser.add_argument(
        '--timeline',
        action='store_true',
        help='Work with timeline clips instead of media pool'
    )

    # Actions
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show color distribution statistics'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List clips by color (use with --color)'
    )

    parser.add_argument(
        '--set-color',
        type=str,
        metavar='COLOR',
        help='Set color on clips'
    )

    parser.add_argument(
        '--clear-color',
        action='store_true',
        help='Clear color from clips'
    )

    # Options
    parser.add_argument(
        '--color',
        type=str,
        metavar='COLOR',
        help='Specify color (use with --list or --clear-color)'
    )

    parser.add_argument(
        '--search',
        type=str,
        metavar='QUERY',
        help='Filter clips by name (use with --set-color)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Need at least one action
    if not any([args.stats, args.list, args.set_color, args.clear_color]):
        parser.print_help()
        return

    # Validation
    if args.list and not args.color:
        print("❌ --list requires --color")
        sys.exit(1)

    if args.set_color and args.set_color not in CLIP_COLORS:
        print(f"❌ Invalid color: {args.set_color}")
        print(f"   Available colors: {', '.join(CLIP_COLORS)}")
        sys.exit(1)

    print("=" * 70)
    print("DaVinci Resolve Clip Color Manager")
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

        print(f"✅ Connected to project: {project.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Get clips
    if args.timeline:
        timeline = project.GetCurrentTimeline()

        if not timeline:
            print("❌ No timeline is currently open")
            sys.exit(1)

        print(f"Working with timeline: {timeline.GetName()}")
        clips = get_clips_from_timeline(timeline)
        print(f"Found {len(clips)} clip(s) in timeline")
    else:
        media_pool = project.GetMediaPool()

        if not media_pool:
            print("❌ Could not access media pool")
            sys.exit(1)

        print("Working with media pool")
        clips = get_all_clips_from_media_pool(media_pool)
        print(f"Found {len(clips)} clip(s) in media pool")

    print()

    # Execute actions
    if args.stats:
        color_counts = get_color_statistics(clips)
        print_color_statistics(color_counts, len(clips))

    if args.list:
        list_clips_by_color(clips, args.color)

    if args.set_color:
        updated = set_clip_color(clips, args.set_color, args.search, dry_run=args.dry_run)

        print()
        print("=" * 70)

        if args.dry_run:
            print(f"Would update {updated} clip(s)")
        else:
            print(f"✅ Updated {updated} clip(s)")

        print("=" * 70)

    if args.clear_color:
        cleared = clear_clip_color(clips, args.color, dry_run=args.dry_run)

        print()
        print("=" * 70)

        if args.dry_run:
            print(f"Would clear {cleared} clip(s)")
        else:
            print(f"✅ Cleared {cleared} clip(s)")

        print("=" * 70)


if __name__ == "__main__":
    main()
