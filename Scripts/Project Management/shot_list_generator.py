#!/usr/bin/env python3
"""
Shot List Generator for DaVinci Resolve

Generate detailed shot lists from timeline with clip information,
timecodes, markers, and metadata. Export to CSV, JSON, or Markdown.

Usage:
    # Generate shot list in CSV format
    python3 shot_list_generator.py --output shots.csv --format csv

    # Generate with markers only
    python3 shot_list_generator.py --output shots.csv --markers-only

    # Generate for specific track
    python3 shot_list_generator.py --output shots.csv --track 1

    # Generate detailed report in Markdown
    python3 shot_list_generator.py --output report.md --format markdown --detailed

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import csv
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def frames_to_timecode(frames: int, fps: int = 24) -> str:
    """
    Convert frame count to timecode.

    Args:
        frames: Frame count
        fps: Frames per second

    Returns:
        Timecode string (HH:MM:SS:FF)
    """
    hours = frames // (3600 * fps)
    frames %= (3600 * fps)

    minutes = frames // (60 * fps)
    frames %= (60 * fps)

    seconds = frames // fps
    frames %= fps

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


def get_clip_info(clip, timeline_fps: int = 24) -> Dict[str, Any]:
    """
    Get detailed information about a clip.

    Args:
        clip: TimelineItem object
        timeline_fps: Timeline frame rate

    Returns:
        Dictionary with clip information
    """
    info = {}

    try:
        # Basic info
        info['name'] = clip.GetName()
        info['duration'] = clip.GetDuration()
        info['start'] = clip.GetStart()
        info['end'] = clip.GetEnd()

        # Timecodes
        info['start_tc'] = frames_to_timecode(info['start'], timeline_fps)
        info['end_tc'] = frames_to_timecode(info['end'], timeline_fps)
        info['duration_tc'] = frames_to_timecode(info['duration'], timeline_fps)

        # Clip color
        info['color'] = clip.GetClipColor() or 'None'

        # Get metadata
        try:
            metadata = clip.GetMetadata()
            if isinstance(metadata, dict):
                # TimelineItem API
                info['scene'] = metadata.get('Scene', '')
                info['shot'] = metadata.get('Shot', '')
                info['take'] = metadata.get('Take', '')
                info['description'] = metadata.get('Description', '')
                info['comments'] = metadata.get('Comments', '')
            else:
                # MediaPoolItem API
                try:
                    info['scene'] = clip.GetMetadata('Scene') or ''
                    info['shot'] = clip.GetMetadata('Shot') or ''
                    info['take'] = clip.GetMetadata('Take') or ''
                    info['description'] = clip.GetMetadata('Description') or ''
                    info['comments'] = clip.GetMetadata('Comments') or ''
                except:
                    info['scene'] = ''
                    info['shot'] = ''
                    info['take'] = ''
                    info['description'] = ''
                    info['comments'] = ''
        except:
            info['scene'] = ''
            info['shot'] = ''
            info['take'] = ''
            info['description'] = ''
            info['comments'] = ''

        # Get markers
        markers = clip.GetMarkers()
        info['markers'] = []

        if markers:
            for frame_id, marker_data in markers.items():
                info['markers'].append({
                    'frame': frame_id,
                    'timecode': frames_to_timecode(frame_id, timeline_fps),
                    'color': marker_data.get('color', 'Blue'),
                    'name': marker_data.get('name', ''),
                    'note': marker_data.get('note', '')
                })

        info['marker_count'] = len(info['markers'])

    except Exception as e:
        print(f"Error getting clip info: {e}")
        info['error'] = str(e)

    return info


def generate_shot_list(
    timeline,
    target_track: Optional[int] = None,
    markers_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Generate shot list from timeline.

    Args:
        timeline: Timeline object
        target_track: Specific track to analyze (None for all)
        markers_only: Only include clips with markers

    Returns:
        List of shot dictionaries
    """
    shots = []

    try:
        # Get timeline FPS
        timeline_fps = int(timeline.GetSetting('timelineFrameRate') or 24)
    except:
        timeline_fps = 24

    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        if target_track and track_index != target_track:
            continue

        items = timeline.GetItemListInTrack('video', track_index)

        if items:
            for item in items:
                clip_info = get_clip_info(item, timeline_fps)
                clip_info['track'] = track_index

                # Filter by markers if requested
                if markers_only and clip_info['marker_count'] == 0:
                    continue

                shots.append(clip_info)

    return shots


def export_csv(shots: List[Dict[str, Any]], output_path: str, detailed: bool = False) -> bool:
    """
    Export shot list to CSV.

    Args:
        shots: List of shot dictionaries
        output_path: Output file path
        detailed: Include detailed information

    Returns:
        True if successful
    """
    try:
        if detailed:
            fieldnames = [
                'track', 'name', 'start_tc', 'end_tc', 'duration_tc',
                'scene', 'shot', 'take', 'color', 'marker_count',
                'description', 'comments'
            ]
        else:
            fieldnames = [
                'track', 'name', 'start_tc', 'duration_tc',
                'scene', 'shot', 'color', 'marker_count'
            ]

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

            writer.writeheader()

            for shot in shots:
                writer.writerow(shot)

        return True

    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False


def export_json(shots: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export shot list to JSON.

    Args:
        shots: List of shot dictionaries
        output_path: Output file path

    Returns:
        True if successful
    """
    try:
        with open(output_path, 'w') as jsonfile:
            json.dump(shots, jsonfile, indent=2)

        return True

    except Exception as e:
        print(f"Error exporting JSON: {e}")
        return False


def export_markdown(
    shots: List[Dict[str, Any]],
    output_path: str,
    timeline_name: str,
    detailed: bool = False
) -> bool:
    """
    Export shot list to Markdown.

    Args:
        shots: List of shot dictionaries
        output_path: Output file path
        timeline_name: Timeline name
        detailed: Include detailed information

    Returns:
        True if successful
    """
    try:
        with open(output_path, 'w') as mdfile:
            # Header
            mdfile.write(f"# Shot List: {timeline_name}\n\n")
            mdfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            mdfile.write(f"Total Shots: {len(shots)}\n\n")
            mdfile.write("---\n\n")

            # Shot list
            for idx, shot in enumerate(shots, 1):
                mdfile.write(f"## Shot {idx}: {shot['name']}\n\n")

                mdfile.write(f"- **Track:** {shot['track']}\n")
                mdfile.write(f"- **Timecode:** {shot['start_tc']} - {shot['end_tc']}\n")
                mdfile.write(f"- **Duration:** {shot['duration_tc']}\n")

                if shot.get('scene'):
                    mdfile.write(f"- **Scene:** {shot['scene']}\n")

                if shot.get('shot'):
                    mdfile.write(f"- **Shot:** {shot['shot']}\n")

                if shot.get('take'):
                    mdfile.write(f"- **Take:** {shot['take']}\n")

                if shot.get('color') and shot['color'] != 'None':
                    mdfile.write(f"- **Color:** {shot['color']}\n")

                if shot.get('marker_count') > 0:
                    mdfile.write(f"- **Markers:** {shot['marker_count']}\n")

                if detailed:
                    if shot.get('description'):
                        mdfile.write(f"\n**Description:**\n{shot['description']}\n")

                    if shot.get('comments'):
                        mdfile.write(f"\n**Comments:**\n{shot['comments']}\n")

                    if shot.get('markers'):
                        mdfile.write("\n**Markers:**\n\n")
                        for marker in shot['markers']:
                            mdfile.write(f"- {marker['timecode']} [{marker['color']}]")
                            if marker['name']:
                                mdfile.write(f" - {marker['name']}")
                            if marker['note']:
                                mdfile.write(f": {marker['note']}")
                            mdfile.write("\n")

                mdfile.write("\n---\n\n")

        return True

    except Exception as e:
        print(f"Error exporting Markdown: {e}")
        return False


def print_summary(shots: List[Dict[str, Any]]) -> None:
    """
    Print shot list summary.

    Args:
        shots: List of shot dictionaries
    """
    total_shots = len(shots)
    total_markers = sum(shot.get('marker_count', 0) for shot in shots)

    # Count by track
    tracks = {}
    for shot in shots:
        track = shot['track']
        tracks[track] = tracks.get(track, 0) + 1

    # Count by color
    colors = {}
    for shot in shots:
        color = shot.get('color', 'None')
        colors[color] = colors.get(color, 0) + 1

    print("Shot List Summary:")
    print(f"  Total shots: {total_shots}")
    print(f"  Total markers: {total_markers}")
    print()

    print("Shots by track:")
    for track in sorted(tracks.keys()):
        print(f"  Track {track}: {tracks[track]} shots")
    print()

    print("Shots by color:")
    for color in sorted(colors.keys()):
        print(f"  {color}: {colors[color]} shots")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate shot list from DaVinci Resolve timeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate CSV shot list
  %(prog)s --output shots.csv --format csv

  # Generate detailed Markdown report
  %(prog)s --output report.md --format markdown --detailed

  # Generate JSON for specific track
  %(prog)s --output track1.json --format json --track 1

  # Only clips with markers
  %(prog)s --output marked.csv --markers-only

  # Summary only (no file output)
  %(prog)s --summary

Formats:
  - CSV: Spreadsheet-compatible, good for databases
  - JSON: Structured data, good for programming
  - Markdown: Human-readable report, good for documentation
        """
    )

    # Output options
    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Output file path'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'json', 'markdown', 'md'],
        default='csv',
        help='Output format (default: csv)'
    )

    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed information (descriptions, comments, markers)'
    )

    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print summary only (no file output)'
    )

    # Filtering options
    parser.add_argument(
        '--track',
        type=int,
        metavar='N',
        help='Only analyze specific video track'
    )

    parser.add_argument(
        '--markers-only',
        action='store_true',
        help='Only include clips with markers'
    )

    args = parser.parse_args()

    # Validation
    if not args.summary and not args.output:
        print("Error: Specify --output or --summary")
        sys.exit(1)

    # Normalize format
    output_format = args.format
    if output_format == 'md':
        output_format = 'markdown'

    print("=" * 70)
    print("DaVinci Resolve Shot List Generator")
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

        timeline_name = timeline.GetName()

        print(f"✅ Connected to project: {project.GetName()}")
        print(f"✅ Timeline: {timeline_name}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Generate shot list
    print("Analyzing timeline...")
    print()

    shots = generate_shot_list(
        timeline,
        target_track=args.track,
        markers_only=args.markers_only
    )

    if not shots:
        print("❌ No shots found")
        sys.exit(1)

    print(f"Found {len(shots)} shot(s)")
    print()

    # Print summary
    print_summary(shots)

    # Export if requested
    if args.output:
        print(f"Exporting to: {args.output}")
        print(f"Format: {output_format}")
        print()

        success = False

        if output_format == 'csv':
            success = export_csv(shots, args.output, detailed=args.detailed)
        elif output_format == 'json':
            success = export_json(shots, args.output)
        elif output_format == 'markdown':
            success = export_markdown(shots, args.output, timeline_name, detailed=args.detailed)

        print()
        print("=" * 70)

        if success:
            print(f"✅ Successfully exported shot list to: {args.output}")
            print(f"   {len(shots)} shot(s) included")
        else:
            print("❌ Export failed")

        print("=" * 70)


if __name__ == "__main__":
    main()
