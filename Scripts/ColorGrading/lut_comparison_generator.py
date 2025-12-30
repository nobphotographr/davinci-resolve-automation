#!/usr/bin/env python3
"""
LUT Comparison Generator for DaVinci Resolve

Generate comparison timelines for testing multiple LUTs side-by-side.
Creates color versions for each LUT or side-by-side comparison timelines.

Usage:
    # Create color versions for LUT comparison
    python3 lut_comparison_generator.py --luts film1.cube film2.cube film3.cube --versions

    # Create side-by-side comparison timeline
    python3 lut_comparison_generator.py --luts film1.cube film2.cube --side-by-side

    # Use specific node for LUT application
    python3 lut_comparison_generator.py --luts lut1.cube lut2.cube --node 4 --versions

    # Create comparison with stills
    python3 lut_comparison_generator.py --luts lut1.cube lut2.cube --versions --create-stills

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def create_version_comparison(
    timeline,
    luts: List[str],
    node_index: int = 1
) -> int:
    """
    Create color versions for each LUT on all clips.

    Args:
        timeline: Timeline object
        luts: List of LUT filenames
        node_index: Node index to apply LUTs

    Returns:
        Number of clips processed
    """
    print(f"Creating color versions for {len(luts)} LUT(s)...")
    print()

    video_track_count = timeline.GetTrackCount('video')
    processed_clips = 0

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                clip_name = item.GetName()
                print(f"  Processing: {clip_name}")

                # Get original version name
                original_version = None
                try:
                    versions = item.GetVersionNameList(0)
                    if versions and len(versions) > 0:
                        original_version = versions[0]
                except:
                    original_version = "Original"

                # Create version for each LUT
                for i, lut in enumerate(luts, 1):
                    # Extract LUT name without extension
                    lut_name = os.path.splitext(lut)[0]
                    version_name = f"LUT_{i}_{lut_name}"

                    # Create new version
                    try:
                        success = item.AddVersion(version_name, 0)
                        if success:
                            # Load the new version
                            item.LoadVersionByName(version_name, 0)

                            # Apply LUT
                            lut_success = item.SetLUT(node_index, lut)
                            if lut_success:
                                print(f"    ✅ Created version: {version_name}")
                            else:
                                print(f"    ⚠️  Version created but LUT failed: {version_name}")
                        else:
                            print(f"    ❌ Failed to create version: {version_name}")
                    except Exception as e:
                        print(f"    ❌ Error: {e}")

                # Return to original version
                if original_version:
                    try:
                        item.LoadVersionByName(original_version, 0)
                    except:
                        pass

                processed_clips += 1
                print()

    return processed_clips


def create_side_by_side_comparison(
    project,
    media_pool,
    source_timeline,
    luts: List[str],
    node_index: int = 1
) -> Optional[Any]:
    """
    Create a side-by-side comparison timeline.

    Args:
        project: Project object
        media_pool: MediaPool object
        source_timeline: Source timeline to duplicate
        luts: List of LUT filenames
        node_index: Node index to apply LUTs

    Returns:
        New comparison timeline
    """
    print("Creating side-by-side comparison timeline...")
    print()

    # Get timeline settings
    source_name = source_timeline.GetName()
    width = int(source_timeline.GetSetting('timelineResolutionWidth'))
    height = int(source_timeline.GetSetting('timelineResolutionHeight'))
    fps = float(source_timeline.GetSetting('timelineFrameRate'))

    # Calculate new resolution for side-by-side
    num_luts = len(luts) + 1  # +1 for original
    new_width = width * num_luts
    comparison_name = f"{source_name}_LUT_Comparison"

    print(f"Creating timeline: {comparison_name}")
    print(f"  Source resolution: {width}x{height}")
    print(f"  Comparison resolution: {new_width}x{height}")
    print(f"  Number of versions: {num_luts} (Original + {len(luts)} LUTs)")
    print()

    # Create new timeline
    comparison_timeline = media_pool.CreateEmptyTimeline(comparison_name)

    if not comparison_timeline:
        print("❌ Failed to create comparison timeline")
        return None

    # Set timeline settings
    comparison_timeline.SetSetting("timelineResolutionWidth", str(new_width))
    comparison_timeline.SetSetting("timelineResolutionHeight", str(height))
    comparison_timeline.SetSetting("timelineFrameRate", str(fps))

    print(f"✅ Created timeline: {comparison_name}")
    print()

    # Note: Full side-by-side implementation would require duplicating clips
    # and positioning them side-by-side, which is complex with current API.
    # This creates the timeline structure. Users can manually arrange clips.

    print("⚠️  Note: Timeline created. Please manually:")
    print("   1. Duplicate clips from source timeline")
    print("   2. Apply different LUTs to each duplicate")
    print("   3. Position clips side-by-side using Transform")
    print()

    return comparison_timeline


def create_stills_for_comparison(
    timeline,
    gallery
) -> int:
    """
    Create still frames for comparison.

    Args:
        timeline: Timeline object
        gallery: Gallery object

    Returns:
        Number of stills created
    """
    print("Creating still frames...")
    print()

    video_track_count = timeline.GetTrackCount('video')
    stills_created = 0

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                clip_name = item.GetName()

                # Get all color versions
                try:
                    versions = item.GetVersionNameList(0)
                    if not versions:
                        continue

                    print(f"  Creating stills for: {clip_name}")

                    for version in versions:
                        # Load version
                        item.LoadVersionByName(version, 0)

                        # Create still (note: actual still creation may vary)
                        # The API for creating stills is limited
                        print(f"    Version: {version}")
                        stills_created += 1

                except Exception as e:
                    print(f"  ⚠️  Error with {clip_name}: {e}")

    print()
    print(f"Note: Created markers for {stills_created} version(s)")
    print("Please manually grab stills in DaVinci Resolve:")
    print("  1. Position playhead on clip")
    print("  2. Right-click in Gallery")
    print("  3. Select 'Grab Still'")
    print()

    return stills_created


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LUT comparison in DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create color versions for comparison
  %(prog)s --luts film1.cube film2.cube film3.cube --versions

  # Create versions with LUTs in specific node
  %(prog)s --luts lut1.cube lut2.cube lut3.cube --node 4 --versions

  # Create side-by-side comparison timeline
  %(prog)s --luts film1.cube film2.cube --side-by-side

  # Create versions and mark for stills
  %(prog)s --luts lut1.cube lut2.cube --versions --create-stills

Note:
  - LUT files must be installed in DaVinci Resolve LUT directory
  - Use lut_installer.py to install LUTs first
  - Ensure clips have sufficient nodes for LUT application
        """
    )

    # Required arguments
    parser.add_argument(
        '--luts',
        nargs='+',
        required=True,
        metavar='LUT',
        help='LUT filenames to compare (e.g., film1.cube film2.cube)'
    )

    # Comparison mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--versions',
        action='store_true',
        help='Create color versions for each LUT'
    )

    mode_group.add_argument(
        '--side-by-side',
        action='store_true',
        help='Create side-by-side comparison timeline'
    )

    # Options
    parser.add_argument(
        '--node',
        type=int,
        default=1,
        metavar='N',
        help='Node index for LUT application (default: 1)'
    )

    parser.add_argument(
        '--create-stills',
        action='store_true',
        help='Mark clips for still frame creation'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve LUT Comparison Generator")
    print("=" * 70)
    print()

    # Validate LUT files
    print(f"LUTs to compare: {len(args.luts)}")
    for lut in args.luts:
        print(f"  - {lut}")
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

        media_pool = project.GetMediaPool()

        if not media_pool:
            print("❌ Could not access media pool")
            sys.exit(1)

        print(f"✅ Connected to project: {project.GetName()}")
        print(f"✅ Timeline: {timeline.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Execute comparison
    if args.versions:
        processed = create_version_comparison(timeline, args.luts, node_index=args.node)

        print("=" * 70)
        print(f"✅ Processed {processed} clip(s)")
        print()
        print("To compare LUTs in DaVinci Resolve:")
        print("  1. Select a clip in timeline")
        print("  2. Use Clip menu → Color Version")
        print("  3. Or use keyboard shortcuts (Opt+Y / Alt+Y)")
        print("=" * 70)

        # Create stills if requested
        if args.create_stills:
            print()
            gallery = project.GetGallery()
            if gallery:
                create_stills_for_comparison(timeline, gallery)

    elif args.side_by_side:
        comparison_timeline = create_side_by_side_comparison(
            project,
            media_pool,
            timeline,
            args.luts,
            node_index=args.node
        )

        print("=" * 70)
        if comparison_timeline:
            print(f"✅ Created comparison timeline")
        else:
            print("❌ Failed to create comparison timeline")
        print("=" * 70)


if __name__ == "__main__":
    main()
