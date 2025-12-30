#!/usr/bin/env python3
"""
Conform Assistant for DaVinci Resolve

Assist with conforming (matching) timelines between different versions,
comparing EDLs, and identifying missing or changed clips.

Usage:
    # Compare two timelines
    python3 conform_assistant.py --compare --timeline1 "Edit_v1" --timeline2 "Edit_v2"

    # Find missing clips
    python3 conform_assistant.py --find-missing --output missing_clips.txt

    # Check for clip name changes
    python3 conform_assistant.py --check-renames --output renames.csv

    # Generate conform report
    python3 conform_assistant.py --report conform_report.md

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import csv
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def get_timeline_clips(timeline) -> List[Dict[str, Any]]:
    """
    Get all clips from timeline with their properties.

    Args:
        timeline: Timeline object

    Returns:
        List of clip dictionaries
    """
    clips = []
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)

        if items:
            for item in items:
                clip_info = {
                    'name': item.GetName(),
                    'track': track_index,
                    'start': item.GetStart(),
                    'end': item.GetEnd(),
                    'duration': item.GetDuration(),
                }

                # Try to get media pool item
                try:
                    media_item = item.GetMediaPoolItem()
                    if media_item:
                        clip_props = media_item.GetClipProperty()
                        if clip_props:
                            clip_info['file_path'] = clip_props.get('File Path', '')
                            clip_info['fps'] = clip_props.get('FPS', '')
                except:
                    clip_info['file_path'] = ''
                    clip_info['fps'] = ''

                clips.append(clip_info)

    return clips


def compare_timelines(timeline1, timeline2) -> Dict[str, Any]:
    """
    Compare two timelines and find differences.

    Args:
        timeline1: First timeline
        timeline2: Second timeline

    Returns:
        Dictionary with comparison results
    """
    clips1 = get_timeline_clips(timeline1)
    clips2 = get_timeline_clips(timeline2)

    # Create lookup dictionaries
    clips1_by_name = {clip['name']: clip for clip in clips1}
    clips2_by_name = {clip['name']: clip for clip in clips2}

    # Find differences
    only_in_1 = []
    only_in_2 = []
    changed = []
    same = []

    # Check clips in timeline 1
    for clip in clips1:
        name = clip['name']
        if name not in clips2_by_name:
            only_in_1.append(clip)
        else:
            clip2 = clips2_by_name[name]
            # Check if properties changed
            if (clip['start'] != clip2['start'] or
                clip['duration'] != clip2['duration'] or
                clip['track'] != clip2['track']):
                changed.append({
                    'name': name,
                    'timeline1': clip,
                    'timeline2': clip2
                })
            else:
                same.append(clip)

    # Check clips only in timeline 2
    for clip in clips2:
        name = clip['name']
        if name not in clips1_by_name:
            only_in_2.append(clip)

    return {
        'only_in_timeline1': only_in_1,
        'only_in_timeline2': only_in_2,
        'changed': changed,
        'unchanged': same,
        'total_clips_timeline1': len(clips1),
        'total_clips_timeline2': len(clips2),
    }


def find_missing_media(timeline, media_pool) -> List[Dict[str, Any]]:
    """
    Find clips with missing media files.

    Args:
        timeline: Timeline object
        media_pool: MediaPool object

    Returns:
        List of clips with missing media
    """
    missing = []
    clips = get_timeline_clips(timeline)

    for clip in clips:
        file_path = clip.get('file_path', '')

        if file_path and not os.path.exists(file_path):
            missing.append({
                'name': clip['name'],
                'path': file_path,
                'track': clip['track'],
                'start': clip['start']
            })

    return missing


def detect_renamed_clips(timeline) -> List[Dict[str, Any]]:
    """
    Detect potential clip renames based on file path analysis.

    Args:
        timeline: Timeline object

    Returns:
        List of potential renames
    """
    renames = []
    clips = get_timeline_clips(timeline)

    # Group by file path
    clips_by_path = {}
    for clip in clips:
        path = clip.get('file_path', '')
        if path:
            if path not in clips_by_path:
                clips_by_path[path] = []
            clips_by_path[path].append(clip)

    # Find files with different clip names
    for path, clip_list in clips_by_path.items():
        if len(clip_list) > 1:
            names = set(c['name'] for c in clip_list)
            if len(names) > 1:
                renames.append({
                    'file_path': path,
                    'clip_names': list(names),
                    'occurrences': len(clip_list)
                })

    return renames


def generate_conform_report(
    timeline,
    output_path: str,
    include_missing: bool = True
) -> bool:
    """
    Generate comprehensive conform report.

    Args:
        timeline: Timeline object
        output_path: Output file path
        include_missing: Include missing media check

    Returns:
        True if successful
    """
    try:
        clips = get_timeline_clips(timeline)

        with open(output_path, 'w') as f:
            # Header
            f.write(f"# Conform Report: {timeline.GetName()}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- Total clips: {len(clips)}\n")

            # Track breakdown
            tracks = {}
            for clip in clips:
                track = clip['track']
                tracks[track] = tracks.get(track, 0) + 1

            f.write(f"- Tracks used: {len(tracks)}\n\n")

            f.write("Clips per track:\n")
            for track in sorted(tracks.keys()):
                f.write(f"  - Track {track}: {tracks[track]} clips\n")

            f.write("\n---\n\n")

            # Clip list
            f.write("## Clip List\n\n")
            f.write("| Track | Clip Name | Start | Duration | File Path |\n")
            f.write("|-------|-----------|-------|----------|-----------|\n")

            for clip in clips:
                f.write(f"| {clip['track']} | {clip['name']} | {clip['start']} | ")
                f.write(f"{clip['duration']} | {clip.get('file_path', 'N/A')} |\n")

            # Missing media
            if include_missing:
                f.write("\n---\n\n")
                f.write("## Missing Media Check\n\n")

                missing_count = 0
                for clip in clips:
                    path = clip.get('file_path', '')
                    if path and not os.path.exists(path):
                        if missing_count == 0:
                            f.write("⚠️ The following clips have missing media:\n\n")
                        f.write(f"- **{clip['name']}**\n")
                        f.write(f"  - Track: {clip['track']}\n")
                        f.write(f"  - Path: `{path}`\n\n")
                        missing_count += 1

                if missing_count == 0:
                    f.write("✅ All media files found.\n\n")
                else:
                    f.write(f"\n**Total missing: {missing_count} clip(s)**\n\n")

        return True

    except Exception as e:
        print(f"Error generating report: {e}")
        return False


def export_clip_list_csv(clips: List[Dict[str, Any]], output_path: str) -> bool:
    """
    Export clip list to CSV.

    Args:
        clips: List of clip dictionaries
        output_path: Output file path

    Returns:
        True if successful
    """
    try:
        fieldnames = ['track', 'name', 'start', 'end', 'duration', 'file_path', 'fps']

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()

            for clip in clips:
                writer.writerow(clip)

        return True

    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False


def print_comparison_results(results: Dict[str, Any], name1: str, name2: str) -> None:
    """
    Print timeline comparison results.

    Args:
        results: Comparison results dictionary
        name1: First timeline name
        name2: Second timeline name
    """
    print("=" * 70)
    print(f"Timeline Comparison: {name1} vs {name2}")
    print("=" * 70)
    print()

    print("Summary:")
    print(f"  Timeline 1: {results['total_clips_timeline1']} clips")
    print(f"  Timeline 2: {results['total_clips_timeline2']} clips")
    print(f"  Unchanged: {len(results['unchanged'])} clips")
    print(f"  Changed: {len(results['changed'])} clips")
    print(f"  Only in Timeline 1: {len(results['only_in_timeline1'])} clips")
    print(f"  Only in Timeline 2: {len(results['only_in_timeline2'])} clips")
    print()

    if results['only_in_timeline1']:
        print(f"Clips only in {name1}:")
        for clip in results['only_in_timeline1']:
            print(f"  • {clip['name']} (Track {clip['track']})")
        print()

    if results['only_in_timeline2']:
        print(f"Clips only in {name2}:")
        for clip in results['only_in_timeline2']:
            print(f"  • {clip['name']} (Track {clip['track']})")
        print()

    if results['changed']:
        print("Changed clips:")
        for change in results['changed']:
            print(f"  • {change['name']}")
            clip1 = change['timeline1']
            clip2 = change['timeline2']

            if clip1['start'] != clip2['start']:
                print(f"    Start: {clip1['start']} → {clip2['start']}")
            if clip1['duration'] != clip2['duration']:
                print(f"    Duration: {clip1['duration']} → {clip2['duration']}")
            if clip1['track'] != clip2['track']:
                print(f"    Track: {clip1['track']} → {clip2['track']}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Conform assistant for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate conform report
  %(prog)s --report conform.md

  # Compare two timelines
  %(prog)s --compare --timeline1 "Edit_v1" --timeline2 "Edit_v2"

  # Find missing media
  %(prog)s --find-missing --output missing.txt

  # Export clip list
  %(prog)s --export-clips clips.csv

  # Check for renamed clips
  %(prog)s --check-renames

Use Cases:
  - Match edit to final conform
  - Identify missing media before delivery
  - Compare different edit versions
  - Track clip changes across versions
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--report',
        type=str,
        metavar='FILE',
        help='Generate conform report (Markdown)'
    )

    mode_group.add_argument(
        '--compare',
        action='store_true',
        help='Compare two timelines'
    )

    mode_group.add_argument(
        '--find-missing',
        action='store_true',
        help='Find clips with missing media'
    )

    mode_group.add_argument(
        '--export-clips',
        type=str,
        metavar='FILE',
        help='Export clip list to CSV'
    )

    mode_group.add_argument(
        '--check-renames',
        action='store_true',
        help='Check for renamed clips'
    )

    # Timeline selection for comparison
    parser.add_argument(
        '--timeline1',
        type=str,
        metavar='NAME',
        help='First timeline name (for --compare)'
    )

    parser.add_argument(
        '--timeline2',
        type=str,
        metavar='NAME',
        help='Second timeline name (for --compare)'
    )

    # Output file
    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Output file path'
    )

    args = parser.parse_args()

    # Validation
    if args.compare and (not args.timeline1 or not args.timeline2):
        print("Error: --compare requires --timeline1 and --timeline2")
        sys.exit(1)

    print("=" * 70)
    print("DaVinci Resolve Conform Assistant")
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

    # Get current timeline or specific timelines
    if args.compare:
        # Get timelines by name
        timeline_count = project.GetTimelineCount()
        timeline1 = None
        timeline2 = None

        for i in range(1, timeline_count + 1):
            tl = project.GetTimelineByIndex(i)
            if tl:
                tl_name = tl.GetName()
                if tl_name == args.timeline1:
                    timeline1 = tl
                if tl_name == args.timeline2:
                    timeline2 = tl

        if not timeline1:
            print(f"❌ Timeline not found: {args.timeline1}")
            sys.exit(1)

        if not timeline2:
            print(f"❌ Timeline not found: {args.timeline2}")
            sys.exit(1)

        print(f"Comparing timelines:")
        print(f"  Timeline 1: {args.timeline1}")
        print(f"  Timeline 2: {args.timeline2}")
        print()

        results = compare_timelines(timeline1, timeline2)
        print_comparison_results(results, args.timeline1, args.timeline2)

    else:
        # Use current timeline
        timeline = project.GetCurrentTimeline()

        if not timeline:
            print("❌ No timeline is currently open")
            sys.exit(1)

        timeline_name = timeline.GetName()
        print(f"✅ Timeline: {timeline_name}")
        print()

        if args.report:
            print(f"Generating conform report: {args.report}")
            print()

            success = generate_conform_report(timeline, args.report)

            if success:
                print(f"✅ Successfully generated report: {args.report}")
            else:
                print("❌ Report generation failed")

        elif args.find_missing:
            print("Checking for missing media...")
            print()

            media_pool = project.GetMediaPool()
            missing = find_missing_media(timeline, media_pool)

            if missing:
                print(f"⚠️  Found {len(missing)} clip(s) with missing media:")
                print()

                for clip in missing:
                    print(f"  • {clip['name']}")
                    print(f"    Track: {clip['track']}")
                    print(f"    Path: {clip['path']}")
                    print()

                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(f"Missing Media Report - {timeline_name}\n")
                        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                        for clip in missing:
                            f.write(f"Clip: {clip['name']}\n")
                            f.write(f"Track: {clip['track']}\n")
                            f.write(f"Path: {clip['path']}\n\n")

                    print(f"✅ Missing media list saved to: {args.output}")
            else:
                print("✅ No missing media found")

        elif args.export_clips:
            print(f"Exporting clip list to: {args.export_clips}")
            print()

            clips = get_timeline_clips(timeline)
            success = export_clip_list_csv(clips, args.export_clips)

            if success:
                print(f"✅ Successfully exported {len(clips)} clip(s) to: {args.export_clips}")
            else:
                print("❌ Export failed")

        elif args.check_renames:
            print("Checking for renamed clips...")
            print()

            renames = detect_renamed_clips(timeline)

            if renames:
                print(f"⚠️  Found {len(renames)} file(s) with multiple clip names:")
                print()

                for rename in renames:
                    print(f"  File: {rename['file_path']}")
                    print(f"  Clip names: {', '.join(rename['clip_names'])}")
                    print(f"  Occurrences: {rename['occurrences']}")
                    print()
            else:
                print("✅ No renamed clips detected")

    print("=" * 70)


if __name__ == "__main__":
    main()
