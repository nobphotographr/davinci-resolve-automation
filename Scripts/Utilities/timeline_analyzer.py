#!/usr/bin/env python3
"""
Timeline Analyzer for DaVinci Resolve

Analyzes the current timeline and displays comprehensive statistics including
clip counts, duration, used LUTs, color distribution, and node information.

Usage:
    # Display timeline analysis
    python3 timeline_analyzer.py

    # Export to JSON
    python3 timeline_analyzer.py --json output.json

    # Show detailed per-clip information
    python3 timeline_analyzer.py --detailed

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def format_timecode(frames: int, fps: float) -> str:
    """
    Convert frames to timecode format (HH:MM:SS:FF).

    Args:
        frames: Total frame count
        fps: Frames per second

    Returns:
        Timecode string
    """
    total_seconds = frames / fps
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frame = int(frames % fps)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frame:02d}"


def analyze_clip(clip) -> Dict[str, Any]:
    """
    Analyze a single timeline clip.

    Args:
        clip: TimelineItem object

    Returns:
        Dictionary with clip information
    """
    info = {
        'name': clip.GetName(),
        'duration': clip.GetDuration(),
        'start': clip.GetStart(),
        'end': clip.GetEnd(),
        'color': clip.GetClipColor(),
        'luts': [],
        'node_count': 0
    }

    # Get node graph information
    node_graph = clip.GetNodeGraph()
    if node_graph:
        # Try to get number of nodes (not all API versions support this)
        try:
            info['node_count'] = node_graph.GetNumNodes()
        except AttributeError:
            # Fallback: check nodes 1-10
            for i in range(1, 11):
                lut = clip.GetLUT(i)
                if lut and lut != "":
                    info['node_count'] = max(info['node_count'], i)

    # Get LUTs from nodes
    for node_index in range(1, info['node_count'] + 1):
        lut = clip.GetLUT(node_index)
        if lut and lut != "":
            info['luts'].append({
                'node': node_index,
                'lut': lut
            })

    return info


def analyze_timeline(timeline, detailed: bool = False) -> Dict[str, Any]:
    """
    Analyze complete timeline.

    Args:
        timeline: Timeline object
        detailed: Include per-clip details

    Returns:
        Dictionary with timeline analysis
    """
    analysis = {
        'timeline_name': timeline.GetName(),
        'fps': float(timeline.GetSetting('timelineFrameRate')),
        'resolution': f"{timeline.GetSetting('timelineResolutionWidth')}x{timeline.GetSetting('timelineResolutionHeight')}",
        'start_timecode': timeline.GetStartTimecode(),
        'tracks': {
            'video': timeline.GetTrackCount('video'),
            'audio': timeline.GetTrackCount('audio')
        },
        'clips': {
            'total': 0,
            'by_track': {},
            'by_color': defaultdict(int),
        },
        'duration': {
            'frames': 0,
            'timecode': ''
        },
        'luts': {
            'unique': set(),
            'usage_count': defaultdict(int)
        },
        'nodes': {
            'max_nodes': 0,
            'avg_nodes': 0.0
        }
    }

    if detailed:
        analysis['clip_details'] = []

    total_node_count = 0
    clip_count = 0

    # Analyze video tracks
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)

        if not items:
            analysis['clips']['by_track'][f'V{track_index}'] = 0
            continue

        track_clip_count = len(items)
        analysis['clips']['by_track'][f'V{track_index}'] = track_clip_count
        analysis['clips']['total'] += track_clip_count

        for item in items:
            clip_info = analyze_clip(item)
            clip_count += 1

            # Update color distribution
            color = clip_info['color']
            if color:
                analysis['clips']['by_color'][color] += 1

            # Update LUT statistics
            for lut_info in clip_info['luts']:
                lut_name = lut_info['lut']
                analysis['luts']['unique'].add(lut_name)
                analysis['luts']['usage_count'][lut_name] += 1

            # Update node statistics
            node_count = clip_info['node_count']
            total_node_count += node_count
            analysis['nodes']['max_nodes'] = max(analysis['nodes']['max_nodes'], node_count)

            # Update duration
            duration = clip_info['end'] - clip_info['start']
            analysis['duration']['frames'] = max(analysis['duration']['frames'], clip_info['end'])

            if detailed:
                analysis['clip_details'].append(clip_info)

    # Calculate average nodes
    if clip_count > 0:
        analysis['nodes']['avg_nodes'] = round(total_node_count / clip_count, 2)

    # Format duration
    analysis['duration']['timecode'] = format_timecode(
        analysis['duration']['frames'],
        analysis['fps']
    )

    # Convert sets to lists for JSON serialization
    analysis['luts']['unique'] = sorted(list(analysis['luts']['unique']))
    analysis['luts']['usage_count'] = dict(analysis['luts']['usage_count'])
    analysis['clips']['by_color'] = dict(analysis['clips']['by_color'])

    return analysis


def print_analysis(analysis: Dict[str, Any], detailed: bool = False):
    """
    Print timeline analysis to console.

    Args:
        analysis: Analysis dictionary
        detailed: Show detailed per-clip information
    """
    print("=" * 70)
    print("Timeline Analysis")
    print("=" * 70)
    print()

    # Basic info
    print(f"Timeline: {analysis['timeline_name']}")
    print(f"Resolution: {analysis['resolution']}")
    print(f"Frame Rate: {analysis['fps']} fps")
    print(f"Start Timecode: {analysis['start_timecode']}")
    print(f"Duration: {analysis['duration']['timecode']} ({analysis['duration']['frames']} frames)")
    print()

    # Track info
    print("-" * 70)
    print("Tracks")
    print("-" * 70)
    print(f"Video Tracks: {analysis['tracks']['video']}")
    print(f"Audio Tracks: {analysis['tracks']['audio']}")
    print()

    # Clip statistics
    print("-" * 70)
    print("Clips")
    print("-" * 70)
    print(f"Total Clips: {analysis['clips']['total']}")
    print()

    if analysis['clips']['by_track']:
        print("Clips per Track:")
        for track, count in sorted(analysis['clips']['by_track'].items()):
            print(f"  {track}: {count} clips")
        print()

    if analysis['clips']['by_color']:
        print("Clips by Color:")
        for color, count in sorted(analysis['clips']['by_color'].items()):
            print(f"  {color}: {count} clips")
        print()

    # Node statistics
    print("-" * 70)
    print("Node Statistics")
    print("-" * 70)
    print(f"Maximum Nodes: {analysis['nodes']['max_nodes']}")
    print(f"Average Nodes: {analysis['nodes']['avg_nodes']}")
    print()

    # LUT information
    print("-" * 70)
    print("LUTs")
    print("-" * 70)

    if analysis['luts']['unique']:
        print(f"Unique LUTs: {len(analysis['luts']['unique'])}")
        print()
        print("LUT Usage:")
        for lut in analysis['luts']['unique']:
            count = analysis['luts']['usage_count'][lut]
            print(f"  {lut}: {count} clip(s)")
    else:
        print("No LUTs in use")

    print()

    # Detailed clip information
    if detailed and 'clip_details' in analysis:
        print("-" * 70)
        print("Clip Details")
        print("-" * 70)

        for i, clip in enumerate(analysis['clip_details'], 1):
            print(f"{i}. {clip['name']}")
            print(f"   Duration: {clip['duration']} frames")
            print(f"   Color: {clip['color'] or 'None'}")
            print(f"   Nodes: {clip['node_count']}")

            if clip['luts']:
                print(f"   LUTs:")
                for lut_info in clip['luts']:
                    print(f"     Node {lut_info['node']}: {lut_info['lut']}")

            print()

    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze DaVinci Resolve timeline and display statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --detailed
  %(prog)s --json output.json
  %(prog)s --detailed --json detailed_analysis.json
        """
    )

    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed per-clip information'
    )

    parser.add_argument(
        '--json',
        type=str,
        metavar='FILE',
        help='Export analysis to JSON file'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve Timeline Analyzer")
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
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Analyze timeline
    print("Analyzing timeline...")
    print()

    analysis = analyze_timeline(timeline, detailed=args.detailed)

    # Print results
    print_analysis(analysis, detailed=args.detailed)

    # Export to JSON if requested
    if args.json:
        try:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            print(f"✅ Analysis exported to: {args.json}")
            print()
        except Exception as e:
            print(f"❌ Failed to export JSON: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
