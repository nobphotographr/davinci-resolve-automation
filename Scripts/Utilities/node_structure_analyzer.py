#!/usr/bin/env python3
"""
Node Structure Analyzer for DaVinci Resolve

Analyze node structures in timeline clips to understand grading complexity,
LUT usage, CDL settings, and identify potential issues.

Usage:
    # Analyze all clips in timeline
    python3 node_structure_analyzer.py

    # Analyze with detailed CDL values
    python3 node_structure_analyzer.py --detailed

    # Show only clips with LUTs
    python3 node_structure_analyzer.py --luts-only

    # Export analysis to JSON
    python3 node_structure_analyzer.py --json analysis.json

    # Find anomalies (unusual node counts)
    python3 node_structure_analyzer.py --find-anomalies

    # Analyze specific track
    python3 node_structure_analyzer.py --track 1

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import json
from typing import List, Dict, Optional, Any
from collections import defaultdict

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def analyze_clip_nodes(timeline_item, detailed: bool = False) -> Dict[str, Any]:
    """
    Analyze node structure of a timeline clip.

    Args:
        timeline_item: TimelineItem object
        detailed: Include detailed CDL values

    Returns:
        Dictionary with node analysis
    """
    analysis = {
        'clip_name': timeline_item.GetName(),
        'node_count': 0,
        'nodes': [],
        'luts': [],
        'cdl_nodes': [],
        'has_lut': False,
        'has_cdl': False,
    }

    # Get node count
    try:
        node_count = timeline_item.GetNumNodes()
        analysis['node_count'] = node_count if node_count else 0
    except:
        analysis['node_count'] = 0

    if analysis['node_count'] == 0:
        return analysis

    # Analyze each node
    for node_index in range(1, analysis['node_count'] + 1):
        node_info = {
            'index': node_index,
            'lut': None,
            'cdl': None,
        }

        # Check for LUT
        try:
            lut = timeline_item.GetLUT(node_index)
            if lut and lut != "":
                node_info['lut'] = lut
                analysis['luts'].append({
                    'node': node_index,
                    'lut': lut
                })
                analysis['has_lut'] = True
        except:
            pass

        # Check for CDL
        try:
            cdl_data = timeline_item.GetNodeColorData(node_index)
            if cdl_data:
                # Check if CDL values are non-default
                has_cdl = False

                # Default CDL values
                default_slope = [1.0, 1.0, 1.0, 1.0]
                default_offset = [0.0, 0.0, 0.0, 0.0]
                default_power = [1.0, 1.0, 1.0, 1.0]
                default_saturation = 1.0

                slope = cdl_data.get('slope', default_slope)
                offset = cdl_data.get('offset', default_offset)
                power = cdl_data.get('power', default_power)
                saturation = cdl_data.get('saturation', default_saturation)

                # Check if any values differ from defaults
                if (slope != default_slope or
                    offset != default_offset or
                    power != default_power or
                    saturation != default_saturation):
                    has_cdl = True

                if has_cdl:
                    cdl_info = {
                        'node': node_index,
                    }

                    if detailed:
                        cdl_info['slope'] = slope
                        cdl_info['offset'] = offset
                        cdl_info['power'] = power
                        cdl_info['saturation'] = saturation
                    else:
                        # Just indicate CDL is present
                        cdl_info['has_values'] = True

                    node_info['cdl'] = cdl_info
                    analysis['cdl_nodes'].append(cdl_info)
                    analysis['has_cdl'] = True
        except:
            pass

        analysis['nodes'].append(node_info)

    return analysis


def analyze_timeline(timeline, track_filter: Optional[int] = None) -> Dict[str, Any]:
    """
    Analyze all clips in timeline.

    Args:
        timeline: Timeline object
        track_filter: Optional track number to filter

    Returns:
        Dictionary with complete analysis
    """
    analysis = {
        'timeline_name': timeline.GetName(),
        'clips': [],
        'statistics': {
            'total_clips': 0,
            'total_nodes': 0,
            'clips_with_luts': 0,
            'clips_with_cdl': 0,
            'total_luts': 0,
            'total_cdl_nodes': 0,
            'node_count_distribution': defaultdict(int),
            'lut_usage': defaultdict(int),
        }
    }

    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        # Skip if track filter is set and doesn't match
        if track_filter and track_index != track_filter:
            continue

        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                clip_analysis = analyze_clip_nodes(item, detailed=True)
                clip_analysis['track'] = track_index

                analysis['clips'].append(clip_analysis)

                # Update statistics
                analysis['statistics']['total_clips'] += 1
                analysis['statistics']['total_nodes'] += clip_analysis['node_count']
                analysis['statistics']['node_count_distribution'][clip_analysis['node_count']] += 1

                if clip_analysis['has_lut']:
                    analysis['statistics']['clips_with_luts'] += 1
                    analysis['statistics']['total_luts'] += len(clip_analysis['luts'])

                    # Count LUT usage
                    for lut_info in clip_analysis['luts']:
                        analysis['statistics']['lut_usage'][lut_info['lut']] += 1

                if clip_analysis['has_cdl']:
                    analysis['statistics']['clips_with_cdl'] += 1
                    analysis['statistics']['total_cdl_nodes'] += len(clip_analysis['cdl_nodes'])

    # Convert defaultdict to regular dict for JSON serialization
    analysis['statistics']['node_count_distribution'] = dict(analysis['statistics']['node_count_distribution'])
    analysis['statistics']['lut_usage'] = dict(analysis['statistics']['lut_usage'])

    return analysis


def find_anomalies(analysis: Dict[str, Any], threshold: int = 10) -> List[Dict[str, Any]]:
    """
    Find clips with anomalous node structures.

    Args:
        analysis: Timeline analysis
        threshold: Node count threshold for anomaly detection

    Returns:
        List of anomalous clips
    """
    anomalies = []

    if not analysis['clips']:
        return anomalies

    # Calculate average node count
    total_nodes = analysis['statistics']['total_nodes']
    total_clips = analysis['statistics']['total_clips']
    avg_nodes = total_nodes / total_clips if total_clips > 0 else 0

    for clip in analysis['clips']:
        issues = []

        # Too many nodes
        if clip['node_count'] > threshold:
            issues.append(f"Excessive nodes ({clip['node_count']} nodes)")

        # Significantly above average
        if clip['node_count'] > avg_nodes * 2:
            issues.append(f"Above average ({clip['node_count']} vs avg {avg_nodes:.1f})")

        # No nodes
        if clip['node_count'] == 0:
            issues.append("No nodes")

        # Multiple LUTs on same clip
        if len(clip['luts']) > 2:
            issues.append(f"Multiple LUTs ({len(clip['luts'])})")

        if issues:
            anomalies.append({
                'clip_name': clip['clip_name'],
                'track': clip['track'],
                'node_count': clip['node_count'],
                'issues': issues
            })

    return anomalies


def print_analysis(analysis: Dict[str, Any], detailed: bool = False, luts_only: bool = False):
    """
    Print analysis results.

    Args:
        analysis: Analysis dictionary
        detailed: Show detailed information
        luts_only: Show only clips with LUTs
    """
    print("=" * 70)
    print("Node Structure Analysis")
    print("=" * 70)
    print()

    print(f"Timeline: {analysis['timeline_name']}")
    print()

    # Statistics
    stats = analysis['statistics']
    print("-" * 70)
    print("Statistics")
    print("-" * 70)
    print(f"Total Clips: {stats['total_clips']}")
    print(f"Total Nodes: {stats['total_nodes']}")

    if stats['total_clips'] > 0:
        avg_nodes = stats['total_nodes'] / stats['total_clips']
        print(f"Average Nodes per Clip: {avg_nodes:.1f}")

    print()
    print(f"Clips with LUTs: {stats['clips_with_luts']}")
    print(f"Total LUT Applications: {stats['total_luts']}")
    print(f"Clips with CDL: {stats['clips_with_cdl']}")
    print(f"Total CDL Nodes: {stats['total_cdl_nodes']}")
    print()

    # Node count distribution
    if stats['node_count_distribution']:
        print("Node Count Distribution:")
        for node_count in sorted(stats['node_count_distribution'].keys()):
            clip_count = stats['node_count_distribution'][node_count]
            bar_length = int((clip_count / stats['total_clips']) * 30)
            bar = "█" * bar_length
            print(f"  {node_count:2} nodes: {clip_count:3} clips {bar}")
        print()

    # LUT usage
    if stats['lut_usage']:
        print("LUT Usage:")
        sorted_luts = sorted(stats['lut_usage'].items(), key=lambda x: x[1], reverse=True)
        for lut, count in sorted_luts:
            print(f"  {lut}: {count} clip(s)")
        print()

    # Clip details
    if detailed or luts_only:
        print("-" * 70)
        print("Clips")
        print("-" * 70)

        for clip in analysis['clips']:
            # Skip if luts_only and clip has no LUTs
            if luts_only and not clip['has_lut']:
                continue

            print(f"Clip: {clip['clip_name']}")
            print(f"  Track: V{clip['track']}")
            print(f"  Nodes: {clip['node_count']}")

            if clip['luts']:
                print(f"  LUTs:")
                for lut_info in clip['luts']:
                    print(f"    Node {lut_info['node']}: {lut_info['lut']}")

            if clip['cdl_nodes'] and detailed:
                print(f"  CDL Nodes: {len(clip['cdl_nodes'])}")
                for cdl_info in clip['cdl_nodes']:
                    print(f"    Node {cdl_info['node']}:")
                    if 'slope' in cdl_info:
                        print(f"      Slope: {cdl_info['slope']}")
                        print(f"      Offset: {cdl_info['offset']}")
                        print(f"      Power: {cdl_info['power']}")
                        print(f"      Saturation: {cdl_info['saturation']}")

            print()


def print_anomalies(anomalies: List[Dict[str, Any]]):
    """
    Print anomaly report.

    Args:
        anomalies: List of anomalies
    """
    print("=" * 70)
    print("Anomaly Detection")
    print("=" * 70)
    print()

    if not anomalies:
        print("✅ No anomalies detected")
        print()
        return

    print(f"⚠️  Found {len(anomalies)} anomaly/anomalies")
    print()

    for i, anomaly in enumerate(anomalies, 1):
        print(f"{i}. {anomaly['clip_name']} (Track V{anomaly['track']})")
        print(f"   Nodes: {anomaly['node_count']}")
        print(f"   Issues:")
        for issue in anomaly['issues']:
            print(f"     - {issue}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze node structures in DaVinci Resolve timeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  %(prog)s

  # Detailed analysis with CDL values
  %(prog)s --detailed

  # Show only clips with LUTs
  %(prog)s --luts-only

  # Export to JSON
  %(prog)s --json analysis.json

  # Find anomalies
  %(prog)s --find-anomalies

  # Analyze specific track
  %(prog)s --track 1
        """
    )

    # Options
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed CDL values'
    )

    parser.add_argument(
        '--luts-only',
        action='store_true',
        help='Show only clips with LUTs'
    )

    parser.add_argument(
        '--find-anomalies',
        action='store_true',
        help='Find clips with unusual node structures'
    )

    parser.add_argument(
        '--track',
        type=int,
        metavar='N',
        help='Analyze specific video track only'
    )

    parser.add_argument(
        '--json',
        type=str,
        metavar='FILE',
        help='Export analysis to JSON file'
    )

    parser.add_argument(
        '--threshold',
        type=int,
        default=10,
        metavar='N',
        help='Node count threshold for anomaly detection (default: 10)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve Node Structure Analyzer")
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
            sys.exit(1)

        print(f"✅ Connected to project: {project.GetName()}")
        print(f"✅ Timeline: {timeline.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Analyze timeline
    print("Analyzing node structures...")
    print()

    analysis = analyze_timeline(timeline, track_filter=args.track)

    # Print results
    print_analysis(analysis, detailed=args.detailed, luts_only=args.luts_only)

    # Find anomalies if requested
    if args.find_anomalies:
        anomalies = find_anomalies(analysis, threshold=args.threshold)
        print_anomalies(anomalies)

    # Export to JSON if requested
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"✅ Exported analysis to: {args.json}")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
