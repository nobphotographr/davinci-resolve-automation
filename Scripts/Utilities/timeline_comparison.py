#!/usr/bin/env python3
"""
Timeline Comparison Tool for DaVinci Resolve

Compare multiple timelines and visualize differences in clips, resolution,
frame rate, node structure, LUT usage, and color versions.

Usage:
    # Compare two timelines
    python3 timeline_comparison.py --compare "Timeline1" "Timeline2"

    # Compare with detailed output
    python3 timeline_comparison.py --compare "Timeline1" "Timeline2" --detailed

    # Export comparison to JSON
    python3 timeline_comparison.py --compare "Timeline1" "Timeline2" --json report.json

    # Compare all timelines in project
    python3 timeline_comparison.py --compare-all

    # Show differences only
    python3 timeline_comparison.py --compare "Timeline1" "Timeline2" --diff-only

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import json
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_timeline_info(timeline) -> Dict[str, Any]:
    """
    Get comprehensive timeline information.

    Args:
        timeline: Timeline object

    Returns:
        Dictionary with timeline information
    """
    info = {
        'name': timeline.GetName(),
        'settings': {
            'resolution': f"{timeline.GetSetting('timelineResolutionWidth')}x{timeline.GetSetting('timelineResolutionHeight')}",
            'frame_rate': float(timeline.GetSetting('timelineFrameRate')),
            'start_timecode': timeline.GetStartTimecode(),
        },
        'tracks': {
            'video': timeline.GetTrackCount('video'),
            'audio': timeline.GetTrackCount('audio'),
        },
        'clips': [],
        'statistics': defaultdict(int)
    }

    # Get all video clips
    video_track_count = timeline.GetTrackCount('video')
    total_clips = 0

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                clip_info = analyze_clip(item, track_index)
                info['clips'].append(clip_info)
                total_clips += 1

                # Update statistics
                info['statistics']['total_clips'] += 1
                info['statistics'][f'track_{track_index}_clips'] += 1
                info['statistics']['total_nodes'] += clip_info['node_count']

                if clip_info['luts']:
                    info['statistics']['clips_with_luts'] += 1

                if clip_info['versions']:
                    info['statistics']['clips_with_versions'] += 1

                if clip_info['clip_color']:
                    color = clip_info['clip_color']
                    info['statistics'][f'color_{color}'] += 1

    return info


def analyze_clip(timeline_item, track_index: int) -> Dict[str, Any]:
    """
    Analyze a single timeline clip.

    Args:
        timeline_item: TimelineItem object
        track_index: Track index

    Returns:
        Dictionary with clip information
    """
    clip_info = {
        'name': timeline_item.GetName(),
        'track': track_index,
        'duration': timeline_item.GetDuration(),
        'clip_color': timeline_item.GetClipColor() or None,
        'node_count': 0,
        'luts': [],
        'versions': [],
    }

    # Get node count
    try:
        node_count = timeline_item.GetNumNodes()
        clip_info['node_count'] = node_count if node_count else 0
    except:
        clip_info['node_count'] = 0

    # Get LUT information
    if clip_info['node_count'] > 0:
        for node_index in range(1, clip_info['node_count'] + 1):
            try:
                lut = timeline_item.GetLUT(node_index)
                if lut and lut != "":
                    clip_info['luts'].append({
                        'node': node_index,
                        'lut': lut
                    })
            except:
                pass

    # Get color versions
    try:
        versions = timeline_item.GetVersionNameList(0)
        if versions:
            clip_info['versions'] = versions
    except:
        pass

    return clip_info


def compare_timelines(timeline1_info: Dict[str, Any], timeline2_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two timelines and identify differences.

    Args:
        timeline1_info: First timeline information
        timeline2_info: Second timeline information

    Returns:
        Dictionary with comparison results
    """
    comparison = {
        'timeline1': timeline1_info['name'],
        'timeline2': timeline2_info['name'],
        'differences': [],
        'summary': {
            'identical': True,
            'difference_count': 0
        }
    }

    # Compare settings
    if timeline1_info['settings']['resolution'] != timeline2_info['settings']['resolution']:
        comparison['differences'].append({
            'category': 'settings',
            'field': 'resolution',
            'timeline1': timeline1_info['settings']['resolution'],
            'timeline2': timeline2_info['settings']['resolution']
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    if timeline1_info['settings']['frame_rate'] != timeline2_info['settings']['frame_rate']:
        comparison['differences'].append({
            'category': 'settings',
            'field': 'frame_rate',
            'timeline1': timeline1_info['settings']['frame_rate'],
            'timeline2': timeline2_info['settings']['frame_rate']
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    # Compare track counts
    if timeline1_info['tracks']['video'] != timeline2_info['tracks']['video']:
        comparison['differences'].append({
            'category': 'tracks',
            'field': 'video_tracks',
            'timeline1': timeline1_info['tracks']['video'],
            'timeline2': timeline2_info['tracks']['video']
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    if timeline1_info['tracks']['audio'] != timeline2_info['tracks']['audio']:
        comparison['differences'].append({
            'category': 'tracks',
            'field': 'audio_tracks',
            'timeline1': timeline1_info['tracks']['audio'],
            'timeline2': timeline2_info['tracks']['audio']
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    # Compare clip counts
    clips1 = timeline1_info['statistics']['total_clips']
    clips2 = timeline2_info['statistics']['total_clips']

    if clips1 != clips2:
        comparison['differences'].append({
            'category': 'clips',
            'field': 'total_clips',
            'timeline1': clips1,
            'timeline2': clips2
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    # Compare node counts
    nodes1 = timeline1_info['statistics']['total_nodes']
    nodes2 = timeline2_info['statistics']['total_nodes']

    if nodes1 != nodes2:
        comparison['differences'].append({
            'category': 'nodes',
            'field': 'total_nodes',
            'timeline1': nodes1,
            'timeline2': nodes2
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    # Compare LUT usage
    luts1 = timeline1_info['statistics'].get('clips_with_luts', 0)
    luts2 = timeline2_info['statistics'].get('clips_with_luts', 0)

    if luts1 != luts2:
        comparison['differences'].append({
            'category': 'luts',
            'field': 'clips_with_luts',
            'timeline1': luts1,
            'timeline2': luts2
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    # Compare color version usage
    versions1 = timeline1_info['statistics'].get('clips_with_versions', 0)
    versions2 = timeline2_info['statistics'].get('clips_with_versions', 0)

    if versions1 != versions2:
        comparison['differences'].append({
            'category': 'versions',
            'field': 'clips_with_versions',
            'timeline1': versions1,
            'timeline2': versions2
        })
        comparison['summary']['identical'] = False
        comparison['summary']['difference_count'] += 1

    return comparison


def print_timeline_info(timeline_info: Dict[str, Any], detailed: bool = False):
    """
    Print timeline information.

    Args:
        timeline_info: Timeline information dictionary
        detailed: Show detailed clip information
    """
    print("=" * 70)
    print(f"Timeline: {timeline_info['name']}")
    print("=" * 70)
    print()

    # Settings
    print("Settings:")
    print(f"  Resolution: {timeline_info['settings']['resolution']}")
    print(f"  Frame Rate: {timeline_info['settings']['frame_rate']} fps")
    print(f"  Start Timecode: {timeline_info['settings']['start_timecode']}")
    print()

    # Tracks
    print("Tracks:")
    print(f"  Video Tracks: {timeline_info['tracks']['video']}")
    print(f"  Audio Tracks: {timeline_info['tracks']['audio']}")
    print()

    # Statistics
    print("Statistics:")
    print(f"  Total Clips: {timeline_info['statistics']['total_clips']}")
    print(f"  Total Nodes: {timeline_info['statistics']['total_nodes']}")
    print(f"  Clips with LUTs: {timeline_info['statistics'].get('clips_with_luts', 0)}")
    print(f"  Clips with Versions: {timeline_info['statistics'].get('clips_with_versions', 0)}")
    print()

    # Detailed clip information
    if detailed and timeline_info['clips']:
        print("-" * 70)
        print("Clips:")
        print("-" * 70)
        for i, clip in enumerate(timeline_info['clips'], 1):
            print(f"{i}. {clip['name']}")
            print(f"   Track: V{clip['track']}")
            print(f"   Duration: {clip['duration']} frames")
            print(f"   Nodes: {clip['node_count']}")

            if clip['clip_color']:
                print(f"   Color: {clip['clip_color']}")

            if clip['luts']:
                print(f"   LUTs: {len(clip['luts'])}")
                for lut_info in clip['luts']:
                    print(f"     - Node {lut_info['node']}: {lut_info['lut']}")

            if clip['versions']:
                print(f"   Versions: {', '.join(clip['versions'])}")

            print()


def print_comparison(comparison: Dict[str, Any], detailed: bool = False):
    """
    Print comparison results.

    Args:
        comparison: Comparison results dictionary
        detailed: Show detailed differences
    """
    print("=" * 70)
    print("Timeline Comparison")
    print("=" * 70)
    print()

    print(f"Timeline 1: {comparison['timeline1']}")
    print(f"Timeline 2: {comparison['timeline2']}")
    print()

    if comparison['summary']['identical']:
        print("✅ Timelines are identical")
        print()
        return

    print(f"⚠️  Found {comparison['summary']['difference_count']} difference(s)")
    print()

    if not comparison['differences']:
        return

    print("-" * 70)
    print("Differences:")
    print("-" * 70)
    print()

    # Group differences by category
    categories = defaultdict(list)
    for diff in comparison['differences']:
        categories[diff['category']].append(diff)

    for category, diffs in categories.items():
        print(f"{category.upper()}:")
        for diff in diffs:
            field = diff['field'].replace('_', ' ').title()
            print(f"  {field}:")
            print(f"    {comparison['timeline1']}: {diff['timeline1']}")
            print(f"    {comparison['timeline2']}: {diff['timeline2']}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare DaVinci Resolve timelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two timelines
  %(prog)s --compare "Timeline1" "Timeline2"

  # Compare with detailed output
  %(prog)s --compare "Timeline1" "Timeline2" --detailed

  # Export to JSON
  %(prog)s --compare "Timeline1" "Timeline2" --json comparison.json

  # Show differences only
  %(prog)s --compare "Timeline1" "Timeline2" --diff-only

  # Compare all timelines
  %(prog)s --compare-all
        """
    )

    # Actions
    parser.add_argument(
        '--compare',
        nargs=2,
        metavar=('TIMELINE1', 'TIMELINE2'),
        help='Compare two timelines by name'
    )

    parser.add_argument(
        '--compare-all',
        action='store_true',
        help='Compare all timelines in project'
    )

    # Options
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed clip information'
    )

    parser.add_argument(
        '--diff-only',
        action='store_true',
        help='Show only differences (no full timeline info)'
    )

    parser.add_argument(
        '--json',
        type=str,
        metavar='FILE',
        help='Export comparison to JSON file'
    )

    args = parser.parse_args()

    # Need at least one action
    if not any([args.compare, args.compare_all]):
        parser.print_help()
        return

    print("=" * 70)
    print("DaVinci Resolve Timeline Comparison Tool")
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

    # Get timeline count
    timeline_count = project.GetTimelineCount()

    if timeline_count == 0:
        print("❌ No timelines found in project")
        sys.exit(1)

    print(f"Found {timeline_count} timeline(s)")
    print()

    # Compare specific timelines
    if args.compare:
        timeline1_name, timeline2_name = args.compare

        # Find timelines
        timeline1 = None
        timeline2 = None

        for i in range(1, timeline_count + 1):
            timeline = project.GetTimelineByIndex(i)
            if timeline.GetName() == timeline1_name:
                timeline1 = timeline
            if timeline.GetName() == timeline2_name:
                timeline2 = timeline

        if not timeline1:
            print(f"❌ Timeline not found: {timeline1_name}")
            sys.exit(1)

        if not timeline2:
            print(f"❌ Timeline not found: {timeline2_name}")
            sys.exit(1)

        # Analyze timelines
        print("Analyzing timelines...")
        print()

        timeline1_info = get_timeline_info(timeline1)
        timeline2_info = get_timeline_info(timeline2)

        # Print individual timeline info if not diff-only
        if not args.diff_only:
            print_timeline_info(timeline1_info, detailed=args.detailed)
            print()
            print_timeline_info(timeline2_info, detailed=args.detailed)
            print()

        # Compare
        comparison = compare_timelines(timeline1_info, timeline2_info)
        print_comparison(comparison, detailed=args.detailed)

        # Export to JSON if requested
        if args.json:
            export_data = {
                'timeline1': timeline1_info,
                'timeline2': timeline2_info,
                'comparison': comparison
            }

            with open(args.json, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"✅ Exported comparison to: {args.json}")
            print()

    # Compare all timelines
    elif args.compare_all:
        print("Analyzing all timelines...")
        print()

        all_timelines = []

        for i in range(1, timeline_count + 1):
            timeline = project.GetTimelineByIndex(i)
            timeline_info = get_timeline_info(timeline)
            all_timelines.append(timeline_info)

        # Print all timeline summaries
        for timeline_info in all_timelines:
            print(f"Timeline: {timeline_info['name']}")
            print(f"  Resolution: {timeline_info['settings']['resolution']}")
            print(f"  Frame Rate: {timeline_info['settings']['frame_rate']} fps")
            print(f"  Clips: {timeline_info['statistics']['total_clips']}")
            print(f"  Nodes: {timeline_info['statistics']['total_nodes']}")
            print()

        # Export to JSON if requested
        if args.json:
            with open(args.json, 'w') as f:
                json.dump(all_timelines, f, indent=2)

            print(f"✅ Exported all timeline data to: {args.json}")
            print()

    print("=" * 70)


if __name__ == "__main__":
    main()
