#!/usr/bin/env python3
"""
Batch Timeline Creator for DaVinci Resolve

Create multiple timelines with specified settings and automatically
populate them with media pool clips.

Usage:
    # Create single timeline
    python3 batch_timeline_creator.py --name "My Timeline" --fps 24 --resolution 1920x1080

    # Create multiple timelines from template
    python3 batch_timeline_creator.py --count 5 --prefix "Scene" --fps 24

    # Create timeline and add clips from bin
    python3 batch_timeline_creator.py --name "Edit" --bin "Footage" --add-clips

    # Create with custom settings
    python3 batch_timeline_creator.py --name "4K Timeline" --resolution 3840x2160 --fps 30

    # Dry run to preview
    python3 batch_timeline_creator.py --count 3 --prefix "Test" --dry-run

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any, Tuple

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Common timeline presets
TIMELINE_PRESETS = {
    'hd_24': {
        'resolution': '1920x1080',
        'fps': 24.0,
        'description': 'HD 1920x1080 @ 24 fps (Cinema)'
    },
    'hd_30': {
        'resolution': '1920x1080',
        'fps': 30.0,
        'description': 'HD 1920x1080 @ 30 fps'
    },
    '4k_24': {
        'resolution': '3840x2160',
        'fps': 24.0,
        'description': '4K UHD @ 24 fps (Cinema)'
    },
    '4k_30': {
        'resolution': '3840x2160',
        'fps': 30.0,
        'description': '4K UHD @ 30 fps'
    },
    '4k_60': {
        'resolution': '3840x2160',
        'fps': 60.0,
        'description': '4K UHD @ 60 fps'
    },
}


def parse_resolution(resolution_str: str) -> Tuple[int, int]:
    """
    Parse resolution string into width and height.

    Args:
        resolution_str: Resolution in format "WIDTHxHEIGHT"

    Returns:
        Tuple of (width, height)
    """
    try:
        parts = resolution_str.split('x')
        if len(parts) != 2:
            raise ValueError(f"Invalid resolution format: {resolution_str}")

        width = int(parts[0])
        height = int(parts[1])

        return (width, height)
    except Exception as e:
        raise ValueError(f"Invalid resolution: {resolution_str}") from e


def create_timeline(
    project,
    media_pool,
    name: str,
    resolution: str,
    fps: float,
    dry_run: bool = False
) -> Optional[Any]:
    """
    Create a new timeline with specified settings.

    Args:
        project: Project object
        media_pool: MediaPool object
        name: Timeline name
        resolution: Resolution as "WIDTHxHEIGHT"
        fps: Frame rate
        dry_run: If True, don't actually create timeline

    Returns:
        Timeline object if successful
    """
    width, height = parse_resolution(resolution)

    if dry_run:
        print(f"  Would create: {name}")
        print(f"    Resolution: {resolution}")
        print(f"    Frame Rate: {fps} fps")
        return None

    # Create timeline settings
    timeline_settings = {
        "timelineResolutionWidth": str(width),
        "timelineResolutionHeight": str(height),
        "timelineFrameRate": str(fps),
    }

    # Create timeline
    timeline = media_pool.CreateEmptyTimeline(name)

    if timeline:
        # Apply settings
        for key, value in timeline_settings.items():
            timeline.SetSetting(key, value)

        print(f"  ✅ Created: {name}")
        print(f"    Resolution: {resolution}")
        print(f"    Frame Rate: {fps} fps")
        return timeline
    else:
        print(f"  ❌ Failed to create: {name}")
        return None


def get_clips_from_bin(media_pool, bin_name: str) -> List[Any]:
    """
    Get all clips from a specific bin.

    Args:
        media_pool: MediaPool object
        bin_name: Name of the bin

    Returns:
        List of clip objects
    """
    clips = []

    def search_bin(folder, target_name: str):
        """Recursively search for bin."""
        if folder.GetName() == target_name:
            return folder

        subfolders = folder.GetSubFolderList()
        if subfolders:
            for subfolder in subfolders:
                result = search_bin(subfolder, target_name)
                if result:
                    return result

        return None

    root_folder = media_pool.GetRootFolder()
    target_bin = search_bin(root_folder, bin_name)

    if target_bin:
        bin_clips = target_bin.GetClipList()
        if bin_clips:
            clips.extend(bin_clips)

    return clips


def add_clips_to_timeline(timeline, clips: List[Any]) -> int:
    """
    Add clips to timeline.

    Args:
        timeline: Timeline object
        clips: List of clip objects

    Returns:
        Number of clips added
    """
    if not clips:
        return 0

    media_pool_items = []
    for clip in clips:
        media_pool_items.append(clip)

    # Append clips to timeline
    added = timeline.AppendToTimeline(media_pool_items)

    return len(added) if added else 0


def list_presets():
    """Print available timeline presets."""
    print("=" * 70)
    print("Available Timeline Presets")
    print("=" * 70)
    print()

    for preset_name, preset_data in TIMELINE_PRESETS.items():
        print(f"{preset_name}:")
        print(f"  {preset_data['description']}")
        print(f"  Resolution: {preset_data['resolution']}")
        print(f"  Frame Rate: {preset_data['fps']} fps")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch create timelines in DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create single timeline
  %(prog)s --name "My Timeline" --fps 24 --resolution 1920x1080

  # Create multiple timelines
  %(prog)s --count 5 --prefix "Scene" --fps 24 --resolution 1920x1080

  # Create from preset
  %(prog)s --name "Edit" --preset hd_24

  # Create and add clips from bin
  %(prog)s --name "Rough Cut" --preset 4k_24 --bin "Raw Footage" --add-clips

  # List presets
  %(prog)s --list-presets

  # Dry run
  %(prog)s --count 3 --prefix "Test" --preset hd_24 --dry-run

Available presets: hd_24, hd_30, 4k_24, 4k_30, 4k_60
        """
    )

    # Timeline name options
    name_group = parser.add_mutually_exclusive_group()
    name_group.add_argument(
        '--name',
        type=str,
        metavar='NAME',
        help='Timeline name (for single timeline)'
    )

    name_group.add_argument(
        '--prefix',
        type=str,
        metavar='PREFIX',
        help='Timeline name prefix (for batch creation)'
    )

    # Batch creation
    parser.add_argument(
        '--count',
        type=int,
        metavar='N',
        help='Number of timelines to create (use with --prefix)'
    )

    # Timeline settings
    preset_group = parser.add_mutually_exclusive_group()
    preset_group.add_argument(
        '--preset',
        type=str,
        choices=list(TIMELINE_PRESETS.keys()),
        help='Use predefined preset'
    )

    preset_group.add_argument(
        '--resolution',
        type=str,
        metavar='WxH',
        help='Resolution (e.g., 1920x1080, 3840x2160)'
    )

    parser.add_argument(
        '--fps',
        type=float,
        metavar='FPS',
        help='Frame rate (e.g., 24, 30, 60)'
    )

    # Clip options
    parser.add_argument(
        '--bin',
        type=str,
        metavar='NAME',
        help='Add clips from this media pool bin'
    )

    parser.add_argument(
        '--add-clips',
        action='store_true',
        help='Add clips from specified bin to timeline'
    )

    # Other options
    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List available timeline presets'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without creating timelines'
    )

    args = parser.parse_args()

    # List presets if requested
    if args.list_presets:
        list_presets()
        return

    # Validation
    if not args.name and not args.prefix:
        parser.print_help()
        print()
        print("Error: Either --name or --prefix is required")
        sys.exit(1)

    if args.prefix and not args.count:
        print("Error: --count is required when using --prefix")
        sys.exit(1)

    if args.count and args.count < 1:
        print("Error: --count must be at least 1")
        sys.exit(1)

    # Determine settings
    if args.preset:
        preset = TIMELINE_PRESETS[args.preset]
        resolution = preset['resolution']
        fps = preset['fps']
    else:
        if not args.resolution or not args.fps:
            print("Error: --resolution and --fps are required (or use --preset)")
            sys.exit(1)
        resolution = args.resolution
        fps = args.fps

    # Validate resolution
    try:
        parse_resolution(resolution)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("=" * 70)
    print("DaVinci Resolve Batch Timeline Creator")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No timelines will be created")
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

    # Get clips from bin if specified
    clips_to_add = []
    if args.bin:
        print(f"Looking for clips in bin: {args.bin}")
        clips_to_add = get_clips_from_bin(media_pool, args.bin)
        if clips_to_add:
            print(f"  Found {len(clips_to_add)} clip(s)")
        else:
            print(f"  ⚠️  No clips found in bin: {args.bin}")
        print()

    # Create timeline(s)
    print("Creating timeline(s)...")
    print()

    created_count = 0

    if args.name:
        # Create single timeline
        timeline = create_timeline(
            project,
            media_pool,
            args.name,
            resolution,
            fps,
            dry_run=args.dry_run
        )

        if timeline and clips_to_add and args.add_clips:
            added = add_clips_to_timeline(timeline, clips_to_add)
            if added > 0:
                print(f"    Added {added} clip(s)")

        if timeline:
            created_count = 1

    else:
        # Create multiple timelines
        for i in range(1, args.count + 1):
            timeline_name = f"{args.prefix}_{i:02d}"

            timeline = create_timeline(
                project,
                media_pool,
                timeline_name,
                resolution,
                fps,
                dry_run=args.dry_run
            )

            if timeline and clips_to_add and args.add_clips:
                added = add_clips_to_timeline(timeline, clips_to_add)
                if added > 0:
                    print(f"    Added {added} clip(s)")

            if timeline:
                created_count += 1

    print()
    print("=" * 70)

    if args.dry_run:
        print(f"Would create {created_count if args.name else args.count} timeline(s)")
    else:
        print(f"✅ Created {created_count} timeline(s)")

    print("=" * 70)


if __name__ == "__main__":
    main()
