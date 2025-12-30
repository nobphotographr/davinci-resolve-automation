#!/usr/bin/env python3
"""
Marker Management Tool for DaVinci Resolve

Manage markers in timeline: list, search, filter by color, export to CSV,
import from CSV, and bulk operations.

Usage:
    # List all markers
    python3 marker_manager.py --list

    # List markers with specific color
    python3 marker_manager.py --list --color Blue

    # Export markers to CSV
    python3 marker_manager.py --export markers.csv

    # Search markers by text
    python3 marker_manager.py --search "review"

    # Delete all markers with specific color
    python3 marker_manager.py --delete --color Red --dry-run

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import csv
from typing import List, Dict, Optional, Any

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Marker colors in DaVinci Resolve
MARKER_COLORS = [
    'Blue', 'Cyan', 'Green', 'Yellow', 'Red', 'Pink',
    'Purple', 'Fuchsia', 'Rose', 'Lavender', 'Sky',
    'Mint', 'Lemon', 'Sand', 'Cocoa', 'Cream'
]


def get_all_markers(timeline) -> List[Dict[str, Any]]:
    """
    Get all markers from timeline.

    Args:
        timeline: Timeline object

    Returns:
        List of marker dictionaries
    """
    markers = []

    try:
        marker_dict = timeline.GetMarkers()

        if marker_dict:
            for frame_id, marker_data in marker_dict.items():
                marker_info = {
                    'frame_id': frame_id,
                    'color': marker_data.get('color', 'Blue'),
                    'name': marker_data.get('name', ''),
                    'note': marker_data.get('note', ''),
                    'duration': marker_data.get('duration', 1),
                }
                markers.append(marker_info)
    except:
        pass

    return markers


def print_markers(markers: List[Dict[str, Any]], color_filter: Optional[str] = None):
    """
    Print marker list.

    Args:
        markers: List of marker dictionaries
        color_filter: Optional color to filter
    """
    print("=" * 70)
    print("Timeline Markers")
    print("=" * 70)
    print()

    if not markers:
        print("No markers found")
        print()
        return

    # Filter by color if specified
    if color_filter:
        markers = [m for m in markers if m['color'].lower() == color_filter.lower()]
        print(f"Filtered by color: {color_filter}")
        print()

    if not markers:
        print(f"No markers found with color: {color_filter}")
        print()
        return

    print(f"Total Markers: {len(markers)}")
    print()

    for i, marker in enumerate(sorted(markers, key=lambda x: x['frame_id']), 1):
        print(f"{i}. Frame {marker['frame_id']} - {marker['color']}")
        if marker['name']:
            print(f"   Name: {marker['name']}")
        if marker['note']:
            print(f"   Note: {marker['note']}")
        if marker['duration'] > 1:
            print(f"   Duration: {marker['duration']} frames")
        print()


def export_markers_to_csv(markers: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export markers to CSV file.

    Args:
        markers: List of marker dictionaries
        output_path: Output CSV file path

    Returns:
        True if successful
    """
    try:
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = ['frame_id', 'color', 'name', 'note', 'duration']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for marker in sorted(markers, key=lambda x: x['frame_id']):
                writer.writerow(marker)

        return True
    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")
        return False


def search_markers(markers: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Search markers by text in name or note.

    Args:
        markers: List of marker dictionaries
        query: Search query

    Returns:
        List of matching markers
    """
    query_lower = query.lower()
    results = []

    for marker in markers:
        name_match = query_lower in marker.get('name', '').lower()
        note_match = query_lower in marker.get('note', '').lower()

        if name_match or note_match:
            results.append(marker)

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage markers in DaVinci Resolve timeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all markers
  %(prog)s --list

  # List markers with specific color
  %(prog)s --list --color Blue

  # Export to CSV
  %(prog)s --export markers.csv

  # Search markers
  %(prog)s --search "review"

Available marker colors:
  Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia,
  Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream
        """
    )

    # Actions
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        '--list',
        action='store_true',
        help='List all markers'
    )

    action_group.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export markers to CSV file'
    )

    action_group.add_argument(
        '--search',
        type=str,
        metavar='QUERY',
        help='Search markers by text'
    )

    # Options
    parser.add_argument(
        '--color',
        type=str,
        metavar='COLOR',
        help='Filter by marker color'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve Marker Management Tool")
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

    # Get all markers
    print("Retrieving markers...")
    markers = get_all_markers(timeline)
    print(f"Found {len(markers)} marker(s)")
    print()

    # Execute action
    if args.list:
        print_markers(markers, color_filter=args.color)

    elif args.export:
        # Apply color filter if specified
        if args.color:
            markers = [m for m in markers if m['color'].lower() == args.color.lower()]
            print(f"Exporting {len(markers)} marker(s) with color: {args.color}")
        else:
            print(f"Exporting {len(markers)} marker(s)")

        success = export_markers_to_csv(markers, args.export)

        if success:
            print(f"✅ Markers exported to: {args.export}")
        else:
            print(f"❌ Failed to export markers")

    elif args.search:
        results = search_markers(markers, args.search)
        print(f"Search query: \"{args.search}\"")
        print()
        print_markers(results, color_filter=args.color)


if __name__ == "__main__":
    main()
