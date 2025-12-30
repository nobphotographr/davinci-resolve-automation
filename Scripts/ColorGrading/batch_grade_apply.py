#!/usr/bin/env python3
"""
Batch Grade Application for DaVinci Resolve

Apply grading operations (DRX templates, LUTs, CDL) to multiple clips
in the current timeline via command-line arguments.

Usage Examples:
    # Apply DRX to all clips in track 1
    python3 batch_grade_apply.py --drx template.drx --track 1

    # Apply LUT to all clips
    python3 batch_grade_apply.py --lut my_lut.cube --node 4 --all

    # Apply both DRX and LUT
    python3 batch_grade_apply.py --drx base.drx --lut film.cube --node 4 --track 1

    # Apply to clips with specific color
    python3 batch_grade_apply.py --lut film.cube --node 4 --color Orange

    # Apply CDL adjustments
    python3 batch_grade_apply.py --cdl-slope "1.2 1.0 1.0" --node 1 --all

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Optional

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_clips_by_color(timeline, color_name: str) -> List:
    """
    Get timeline clips by color.

    Args:
        timeline: Timeline object
        color_name: Clip color to filter (e.g., "Orange", "Blue")

    Returns:
        List of TimelineItem objects
    """
    clips = []

    # Check video tracks
    video_track_count = timeline.GetTrackCount("video")
    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack("video", track_index)
        if items:
            for item in items:
                if item.GetClipColor() == color_name:
                    clips.append(item)

    return clips


def get_clips_by_track(timeline, track_type: str, track_index: int) -> List:
    """
    Get all clips from a specific track.

    Args:
        timeline: Timeline object
        track_type: "video" or "audio"
        track_index: Track number (1-based)

    Returns:
        List of TimelineItem objects
    """
    items = timeline.GetItemListInTrack(track_type, track_index)
    return items if items else []


def get_all_video_clips(timeline) -> List:
    """
    Get all video clips from timeline.

    Args:
        timeline: Timeline object

    Returns:
        List of all video TimelineItem objects
    """
    clips = []
    video_track_count = timeline.GetTrackCount("video")

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack("video", track_index)
        if items:
            clips.extend(items)

    return clips


def apply_drx_to_clips(clips: List, drx_path: str) -> int:
    """
    Apply DRX template to clips.

    Args:
        clips: List of TimelineItem objects
        drx_path: Path to DRX file

    Returns:
        Number of successful applications
    """
    if not os.path.isfile(drx_path):
        print(f"❌ DRX file not found: {drx_path}")
        return 0

    success_count = 0

    for clip in clips:
        graph = clip.GetNodeGraph()
        if graph and graph.ApplyGradeFromDRX(drx_path, 0):
            success_count += 1
            print(f"  ✅ DRX applied: {clip.GetName()}")
        else:
            print(f"  ❌ DRX failed: {clip.GetName()}")

    return success_count


def apply_lut_to_clips(clips: List, lut_filename: str, node_index: int) -> int:
    """
    Apply LUT to clips.

    Args:
        clips: List of TimelineItem objects
        lut_filename: LUT filename (not full path)
        node_index: Node index to apply LUT (1-based)

    Returns:
        Number of successful applications
    """
    success_count = 0

    for clip in clips:
        if clip.SetLUT(node_index, lut_filename):
            success_count += 1
            print(f"  ✅ LUT applied: {clip.GetName()}")
        else:
            print(f"  ❌ LUT failed: {clip.GetName()}")

    return success_count


def apply_cdl_to_clips(
    clips: List,
    node_index: int,
    slope: Optional[str] = None,
    offset: Optional[str] = None,
    power: Optional[str] = None,
    saturation: Optional[str] = None
) -> int:
    """
    Apply CDL values to clips.

    Args:
        clips: List of TimelineItem objects
        node_index: Node index (1-based)
        slope: Slope values "R G B" (e.g., "1.2 1.0 1.0")
        offset: Offset values "R G B"
        power: Power values "R G B"
        saturation: Saturation value (e.g., "1.1")

    Returns:
        Number of successful applications
    """
    cdl_map = {"NodeIndex": str(node_index)}

    if slope:
        cdl_map["Slope"] = slope
    if offset:
        cdl_map["Offset"] = offset
    if power:
        cdl_map["Power"] = power
    if saturation:
        cdl_map["Saturation"] = saturation

    if len(cdl_map) == 1:  # Only NodeIndex
        print("⚠️  No CDL values specified")
        return 0

    success_count = 0

    for clip in clips:
        if clip.SetCDL(cdl_map):
            success_count += 1
            print(f"  ✅ CDL applied: {clip.GetName()}")
        else:
            print(f"  ❌ CDL failed: {clip.GetName()}")

    return success_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch apply grading to DaVinci Resolve timeline clips",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply DRX to all clips in video track 1
  %(prog)s --drx template.drx --track 1

  # Apply LUT to all clips
  %(prog)s --lut my_lut.cube --node 4 --all

  # Apply to orange-colored clips only
  %(prog)s --lut film.cube --node 4 --color Orange

  # Apply CDL adjustments
  %(prog)s --cdl-slope "1.2 1.0 1.0" --cdl-saturation "1.1" --node 1 --all

  # Combine DRX and LUT
  %(prog)s --drx base.drx --lut film.cube --node 4 --track 1
        """
    )

    # Target selection
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '--all',
        action='store_true',
        help='Apply to all video clips in timeline'
    )
    target_group.add_argument(
        '--track',
        type=int,
        metavar='N',
        help='Apply to specific video track number (1-based)'
    )
    target_group.add_argument(
        '--color',
        type=str,
        metavar='COLOR',
        help='Apply to clips with specific color (e.g., Orange, Blue)'
    )

    # Grading operations
    parser.add_argument(
        '--drx',
        type=str,
        metavar='FILE',
        help='DRX template file to apply'
    )

    parser.add_argument(
        '--lut',
        type=str,
        metavar='FILE',
        help='LUT filename to apply (must be in LUT directory)'
    )

    parser.add_argument(
        '--node',
        type=int,
        default=1,
        metavar='N',
        help='Node index for LUT/CDL application (default: 1)'
    )

    # CDL parameters
    parser.add_argument(
        '--cdl-slope',
        type=str,
        metavar='R G B',
        help='CDL Slope values (e.g., "1.2 1.0 1.0")'
    )

    parser.add_argument(
        '--cdl-offset',
        type=str,
        metavar='R G B',
        help='CDL Offset values (e.g., "0.1 0.0 0.0")'
    )

    parser.add_argument(
        '--cdl-power',
        type=str,
        metavar='R G B',
        help='CDL Power values (e.g., "1.0 1.0 1.0")'
    )

    parser.add_argument(
        '--cdl-saturation',
        type=str,
        metavar='VALUE',
        help='CDL Saturation value (e.g., "1.1")'
    )

    args = parser.parse_args()

    # Validate that at least one operation is specified
    if not any([args.drx, args.lut, args.cdl_slope, args.cdl_offset,
                args.cdl_power, args.cdl_saturation]):
        parser.error("At least one grading operation (--drx, --lut, or --cdl-*) is required")

    print("=" * 70)
    print("DaVinci Resolve Batch Grade Application")
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

        timeline = project.GetCurrentTimeline()

        if not timeline:
            print("❌ No timeline is currently open")
            print("   Please open a timeline")
            sys.exit(1)

        print(f"✅ Connected to project: {project.GetName()}")
        print(f"✅ Timeline: {timeline.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Get target clips
    print("Selecting target clips...")

    if args.all:
        clips = get_all_video_clips(timeline)
        print(f"  Target: All video clips ({len(clips)} clips)")
    elif args.track:
        clips = get_clips_by_track(timeline, "video", args.track)
        print(f"  Target: Video track {args.track} ({len(clips)} clips)")
    elif args.color:
        clips = get_clips_by_color(timeline, args.color)
        print(f"  Target: Clips with {args.color} color ({len(clips)} clips)")

    if not clips:
        print("❌ No clips found matching criteria")
        sys.exit(1)

    print()

    # Apply operations
    operations_applied = 0

    # Apply DRX
    if args.drx:
        print(f"Applying DRX template: {args.drx}")
        # Refresh LUT list if we're also applying a LUT
        if args.lut:
            project.RefreshLUTList()
        success = apply_drx_to_clips(clips, args.drx)
        print(f"  Result: {success}/{len(clips)} clips")
        print()
        operations_applied += 1

    # Apply LUT
    if args.lut:
        print(f"Applying LUT: {args.lut} (Node {args.node})")
        # Refresh LUT list
        project.RefreshLUTList()
        success = apply_lut_to_clips(clips, args.lut, args.node)
        print(f"  Result: {success}/{len(clips)} clips")
        print()
        operations_applied += 1

    # Apply CDL
    if any([args.cdl_slope, args.cdl_offset, args.cdl_power, args.cdl_saturation]):
        print(f"Applying CDL (Node {args.node})")
        success = apply_cdl_to_clips(
            clips,
            args.node,
            args.cdl_slope,
            args.cdl_offset,
            args.cdl_power,
            args.cdl_saturation
        )
        print(f"  Result: {success}/{len(clips)} clips")
        print()
        operations_applied += 1

    print("=" * 70)
    print(f"✅ Batch processing complete ({operations_applied} operation(s) applied)")
    print("=" * 70)


if __name__ == "__main__":
    main()
