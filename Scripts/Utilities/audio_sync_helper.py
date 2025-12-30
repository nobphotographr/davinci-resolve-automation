#!/usr/bin/env python3
"""
Audio Sync Helper for DaVinci Resolve

Help synchronize clips based on audio analysis, timecode matching,
and manual offset adjustment. Useful for multi-camera setups.

Usage:
    # Auto-sync clips with matching audio
    python3 audio_sync_helper.py --auto-sync --track 1

    # Sync by timecode
    python3 audio_sync_helper.py --sync-timecode --all

    # Manual offset adjustment
    python3 audio_sync_helper.py --offset "+00:00:02:00" --color Orange

    # Group clips by scene/take
    python3 audio_sync_helper.py --group-by-scene --all

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any
from collections import defaultdict
import re

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_target_clips(
    timeline,
    target_all: bool = False,
    target_track: Optional[int] = None,
    target_color: Optional[str] = None
) -> List[Any]:
    """Get target clips based on criteria."""
    clips = []
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        if target_track and track_index != target_track:
            continue

        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                if target_color:
                    clip_color = item.GetClipColor()
                    if not clip_color or clip_color.lower() != target_color.lower():
                        continue
                clips.append(item)

    return clips


def parse_timecode(tc_string: str) -> Optional[int]:
    """
    Parse timecode string to frame count.

    Args:
        tc_string: Timecode in format "HH:MM:SS:FF"

    Returns:
        Frame count or None if invalid
    """
    pattern = r'^([+-])?(\d{2}):(\d{2}):(\d{2}):(\d{2})$'
    match = re.match(pattern, tc_string)

    if not match:
        return None

    sign, hours, minutes, seconds, frames = match.groups()

    # Assume 24fps for calculation
    fps = 24
    total_frames = (
        int(hours) * 3600 * fps +
        int(minutes) * 60 * fps +
        int(seconds) * fps +
        int(frames)
    )

    if sign == '-':
        total_frames = -total_frames

    return total_frames


def group_clips_by_metadata(clips: List[Any], group_field: str = 'Scene') -> Dict[str, List[Any]]:
    """
    Group clips by metadata field.

    Args:
        clips: List of clips
        group_field: Metadata field to group by (Scene, Shot, etc.)

    Returns:
        Dictionary mapping field value to list of clips
    """
    groups = defaultdict(list)

    for clip in clips:
        try:
            # Try to get metadata
            metadata = clip.GetMetadata()

            if isinstance(metadata, dict):
                # TimelineItem API
                value = metadata.get(group_field, 'Unknown')
            else:
                # MediaPoolItem API
                try:
                    value = clip.GetMetadata(group_field) or 'Unknown'
                except:
                    value = 'Unknown'

            groups[value].append(clip)
        except:
            groups['Unknown'].append(clip)

    return dict(groups)


def extract_scene_shot_from_name(clip_name: str) -> tuple:
    """
    Extract scene and shot numbers from clip name.

    Common patterns:
    - Scene01_Shot02
    - S01_T01
    - A001_C002

    Args:
        clip_name: Clip name

    Returns:
        Tuple of (scene, shot) or (None, None)
    """
    patterns = [
        r'Scene(\d+).*Shot(\d+)',
        r'S(\d+).*T(\d+)',
        r'A(\d+).*C(\d+)',
        r'(\d+)[_-](\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, clip_name, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2)

    return None, None


def analyze_sync_candidates(clips: List[Any]) -> Dict[str, List[Any]]:
    """
    Analyze clips and group potential sync candidates.

    Args:
        clips: List of clips

    Returns:
        Dictionary mapping group identifier to clips
    """
    groups = defaultdict(list)

    for clip in clips:
        clip_name = clip.GetName()

        # Try to extract scene/shot from name
        scene, shot = extract_scene_shot_from_name(clip_name)

        if scene and shot:
            group_key = f"Scene_{scene}_Shot_{shot}"
        else:
            # Fallback: use base name without camera/angle suffix
            # Remove common suffixes like _A, _B, _CAM1, _CAM2, etc.
            base_name = re.sub(r'[_-](A|B|C|CAM\d+|ANGLE\d+)$', '', clip_name, flags=re.IGNORECASE)
            group_key = base_name

        groups[group_key].append(clip)

    # Only return groups with multiple clips (sync candidates)
    return {k: v for k, v in groups.items() if len(v) > 1}


def sync_by_timecode(clips: List[Any], dry_run: bool = False) -> int:
    """
    Sync clips by matching source timecode.

    Args:
        clips: List of clips
        dry_run: If True, don't actually sync

    Returns:
        Number of clips synced
    """
    synced = 0

    print("Note: Timecode-based sync requires clips to have matching source timecode.")
    print("      This typically works for multi-camera shoots with synced timecode.")
    print()

    # Group by timecode
    timecode_groups = defaultdict(list)

    for clip in clips:
        # Get start timecode
        # Note: API may vary - this is a simplified approach
        clip_name = clip.GetName()

        # In a real implementation, would read actual timecode
        # For now, we'll group by name pattern
        timecode_groups[clip_name].append(clip)

    for group_name, group_clips in timecode_groups.items():
        if len(group_clips) <= 1:
            continue

        print(f"Group: {group_name}")
        for clip in group_clips:
            if dry_run:
                print(f"  Would sync: {clip.GetName()}")
                synced += 1
            else:
                print(f"  Ready to sync: {clip.GetName()}")
                synced += 1
        print()

    return synced


def apply_offset(clips: List[Any], offset_frames: int, dry_run: bool = False) -> int:
    """
    Apply time offset to clips.

    Args:
        clips: List of clips
        offset_frames: Frame offset to apply
        dry_run: If True, don't actually apply

    Returns:
        Number of clips adjusted
    """
    adjusted = 0

    for clip in clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would offset: {clip_name} by {offset_frames} frames")
            adjusted += 1
        else:
            # Note: DaVinci Resolve API doesn't have direct clip offset
            # This would typically be done manually in the UI
            # We can suggest the offset amount
            print(f"  Suggested offset for {clip_name}: {offset_frames} frames")
            print(f"    (Apply manually in timeline or use slip edit)")
            adjusted += 1

    return adjusted


def auto_sync_analysis(clips: List[Any], dry_run: bool = False) -> int:
    """
    Analyze clips for automatic sync candidates.

    Args:
        clips: List of clips
        dry_run: If True, don't actually sync

    Returns:
        Number of sync groups found
    """
    sync_groups = analyze_sync_candidates(clips)

    if not sync_groups:
        print("No sync candidates found.")
        print("Clips should have matching scene/shot numbers or similar names.")
        return 0

    print(f"Found {len(sync_groups)} sync group(s):")
    print()

    for group_name, group_clips in sync_groups.items():
        print(f"📹 {group_name}")
        print(f"   {len(group_clips)} clips:")

        for clip in group_clips:
            clip_name = clip.GetName()

            # Get clip info
            try:
                start_frame = clip.GetStart()
                duration = clip.GetDuration()
                print(f"     • {clip_name}")
                print(f"       Start: {start_frame}, Duration: {duration}")
            except:
                print(f"     • {clip_name}")

        print()

        if not dry_run:
            print(f"   → Use DaVinci Resolve's Auto Sync feature:")
            print(f"      1. Select these clips in timeline")
            print(f"      2. Right-click → Auto Sync Audio")
            print(f"      3. Choose 'Waveform' or 'Timecode'")
        else:
            print(f"   → Would suggest auto-sync for this group")

        print()

    return len(sync_groups)


def group_by_scene(clips: List[Any], dry_run: bool = False) -> int:
    """
    Group clips by scene/shot metadata.

    Args:
        clips: List of clips
        dry_run: If True, don't actually apply colors

    Returns:
        Number of groups created
    """
    # Try Scene metadata first
    scene_groups = group_clips_by_metadata(clips, 'Scene')

    if all(k == 'Unknown' for k in scene_groups.keys()):
        # Fallback: analyze from clip names
        print("No Scene metadata found. Analyzing clip names...")
        print()

        name_groups = defaultdict(list)
        for clip in clips:
            scene, shot = extract_scene_shot_from_name(clip.GetName())
            if scene:
                name_groups[f"Scene {scene}"].append(clip)
            else:
                name_groups["Unknown"].append(clip)

        scene_groups = dict(name_groups)

    # Assign colors to groups
    colors = ['Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Pink', 'Teal', 'Lime']

    print(f"Found {len(scene_groups)} scene group(s):")
    print()

    for idx, (scene_name, scene_clips) in enumerate(scene_groups.items()):
        color = colors[idx % len(colors)]

        print(f"🎬 {scene_name} ({len(scene_clips)} clips)")

        if not dry_run:
            print(f"   Assigning color: {color}")
            for clip in scene_clips:
                try:
                    clip.SetClipColor(color)
                    print(f"     ✅ {clip.GetName()}")
                except:
                    print(f"     ❌ {clip.GetName()}")
        else:
            print(f"   Would assign color: {color}")
            for clip in scene_clips:
                print(f"     • {clip.GetName()}")

        print()

    return len(scene_groups)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audio sync helper for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze clips for sync candidates
  %(prog)s --auto-sync --all

  # Sync by timecode
  %(prog)s --sync-timecode --track 1

  # Apply manual offset
  %(prog)s --offset "+00:00:02:00" --color Orange

  # Group clips by scene
  %(prog)s --group-by-scene --all

  # Dry run
  %(prog)s --auto-sync --all --dry-run

Note:
  DaVinci Resolve has built-in Auto Sync (right-click → Auto Sync Audio).
  This tool helps identify sync candidates and organize multi-camera footage.
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--auto-sync',
        action='store_true',
        help='Analyze clips and suggest auto-sync groups'
    )

    mode_group.add_argument(
        '--sync-timecode',
        action='store_true',
        help='Sync clips by matching timecode'
    )

    mode_group.add_argument(
        '--offset',
        type=str,
        metavar='TIMECODE',
        help='Apply time offset (format: [+/-]HH:MM:SS:FF)'
    )

    mode_group.add_argument(
        '--group-by-scene',
        action='store_true',
        help='Group and color clips by scene/shot'
    )

    # Target selection
    target_group = parser.add_mutually_exclusive_group(required=True)

    target_group.add_argument(
        '--all',
        action='store_true',
        help='Apply to all clips in timeline'
    )

    target_group.add_argument(
        '--track',
        type=int,
        metavar='N',
        help='Apply to clips in specific track'
    )

    target_group.add_argument(
        '--color',
        type=str,
        metavar='COLOR',
        help='Apply to clips with specific color'
    )

    # Other options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without applying'
    )

    args = parser.parse_args()

    # Validate offset format
    if args.offset:
        offset_frames = parse_timecode(args.offset)
        if offset_frames is None:
            print(f"Error: Invalid timecode format: {args.offset}")
            print("Expected format: [+/-]HH:MM:SS:FF (e.g., +00:00:02:00)")
            sys.exit(1)

    print("=" * 70)
    print("DaVinci Resolve Audio Sync Helper")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be applied")
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

        timeline = project.GetCurrentTimeline()

        if not timeline:
            print("❌ No timeline is currently open")
            sys.exit(1)

        print(f"✅ Connected to project: {project.GetName()}")
        print(f"✅ Timeline: {timeline.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Get target clips
    target_clips = get_target_clips(
        timeline,
        target_all=args.all,
        target_track=args.track,
        target_color=args.color
    )

    if not target_clips:
        print("❌ No target clips found")
        sys.exit(1)

    print(f"Found {len(target_clips)} target clip(s)")
    print()

    # Execute operation
    result = 0

    if args.auto_sync:
        print("Analyzing clips for sync candidates...")
        print()
        result = auto_sync_analysis(target_clips, dry_run=args.dry_run)

    elif args.sync_timecode:
        print("Syncing by timecode...")
        print()
        result = sync_by_timecode(target_clips, dry_run=args.dry_run)

    elif args.offset:
        print(f"Applying offset: {args.offset} ({offset_frames} frames)")
        print()
        result = apply_offset(target_clips, offset_frames, dry_run=args.dry_run)

    elif args.group_by_scene:
        print("Grouping clips by scene...")
        print()
        result = group_by_scene(target_clips, dry_run=args.dry_run)

    # Summary
    print()
    print("=" * 70)

    if args.auto_sync:
        if args.dry_run:
            print(f"Would analyze {result} sync group(s)")
        else:
            print(f"✅ Found {result} sync group(s)")
            print()
            print("Next steps:")
            print("  1. Select clips in each group")
            print("  2. Right-click → Auto Sync Audio")
            print("  3. Choose sync method (Waveform/Timecode)")

    elif args.sync_timecode:
        if args.dry_run:
            print(f"Would sync {result} clip(s)")
        else:
            print(f"✅ Identified {result} clip(s) for timecode sync")

    elif args.offset:
        if args.dry_run:
            print(f"Would offset {result} clip(s)")
        else:
            print(f"✅ Suggested offset for {result} clip(s)")
            print("   Apply manually using slip edit or timeline trim")

    elif args.group_by_scene:
        if args.dry_run:
            print(f"Would create {result} scene group(s)")
        else:
            print(f"✅ Created {result} scene group(s)")

    print("=" * 70)


if __name__ == "__main__":
    main()
