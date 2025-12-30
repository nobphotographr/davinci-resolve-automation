#!/usr/bin/env python3
"""
Timeline Export/Import Tool for DaVinci Resolve

Export timeline structure and settings to JSON for backup, sharing,
or importing to other projects.

Usage:
    # Export current timeline
    python3 timeline_export_import.py --export timeline_backup.json

    # Export with clip details
    python3 timeline_export_import.py --export timeline_full.json --detailed

    # Import timeline structure (creates new timeline)
    python3 timeline_export_import.py --import timeline_backup.json

    # List all timeline exports
    python3 timeline_export_import.py --list-exports

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import json
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def export_timeline(timeline, detailed: bool = False) -> Dict[str, Any]:
    """
    Export timeline structure and settings.

    Args:
        timeline: Timeline object
        detailed: Include detailed clip information

    Returns:
        Dictionary with timeline data
    """
    export_data = {
        'export_version': '1.0',
        'export_date': datetime.now().isoformat(),
        'timeline': {
            'name': timeline.GetName(),
            'settings': {
                'resolution_width': timeline.GetSetting('timelineResolutionWidth'),
                'resolution_height': timeline.GetSetting('timelineResolutionHeight'),
                'frame_rate': timeline.GetSetting('timelineFrameRate'),
                'start_timecode': timeline.GetStartTimecode(),
            },
            'tracks': {
                'video': timeline.GetTrackCount('video'),
                'audio': timeline.GetTrackCount('audio'),
            },
            'clips': []
        }
    }

    # Export clip information
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                clip_data = {
                    'name': item.GetName(),
                    'track': track_index,
                    'start': item.GetStart(),
                    'end': item.GetEnd(),
                    'duration': item.GetDuration(),
                }

                if detailed:
                    # Add detailed information
                    try:
                        clip_data['clip_color'] = item.GetClipColor()
                        clip_data['node_count'] = item.GetNumNodes()

                        # Get metadata
                        try:
                            metadata = item.GetMetadata()
                            if isinstance(metadata, dict):
                                clip_data['metadata'] = metadata
                        except:
                            pass

                    except:
                        pass

                export_data['timeline']['clips'].append(clip_data)

    return export_data


def validate_import_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate imported timeline data.

    Args:
        data: Import data dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if 'timeline' not in data:
        return (False, "Missing 'timeline' key")

    timeline = data['timeline']

    required_keys = ['name', 'settings', 'tracks']
    for key in required_keys:
        if key not in timeline:
            return (False, f"Missing '{key}' in timeline data")

    return (True, "")


def create_timeline_from_import(
    media_pool,
    import_data: Dict[str, Any]
) -> Optional[Any]:
    """
    Create timeline from import data.

    Args:
        media_pool: MediaPool object
        import_data: Import data dictionary

    Returns:
        Timeline object or None
    """
    timeline_data = import_data['timeline']

    # Generate unique name if needed
    base_name = timeline_data['name']
    timeline_name = f"{base_name}_imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"Creating timeline: {timeline_name}")

    # Create timeline
    timeline = media_pool.CreateEmptyTimeline(timeline_name)

    if not timeline:
        print("❌ Failed to create timeline")
        return None

    # Apply settings
    try:
        settings = timeline_data['settings']
        timeline.SetSetting('timelineResolutionWidth', settings['resolution_width'])
        timeline.SetSetting('timelineResolutionHeight', settings['resolution_height'])
        timeline.SetSetting('timelineFrameRate', settings['frame_rate'])

        print(f"  Resolution: {settings['resolution_width']}x{settings['resolution_height']}")
        print(f"  Frame Rate: {settings['frame_rate']} fps")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not apply all settings: {e}")

    return timeline


def print_timeline_info(export_data: Dict[str, Any]):
    """
    Print timeline information from export data.

    Args:
        export_data: Export data dictionary
    """
    timeline = export_data['timeline']

    print("=" * 70)
    print(f"Timeline: {timeline['name']}")
    print("=" * 70)
    print()

    print(f"Export Date: {export_data.get('export_date', 'Unknown')}")
    print()

    print("Settings:")
    settings = timeline['settings']
    print(f"  Resolution: {settings['resolution_width']}x{settings['resolution_height']}")
    print(f"  Frame Rate: {settings['frame_rate']} fps")
    print(f"  Start Timecode: {settings.get('start_timecode', 'N/A')}")
    print()

    print("Tracks:")
    tracks = timeline['tracks']
    print(f"  Video: {tracks['video']}")
    print(f"  Audio: {tracks['audio']}")
    print()

    print(f"Clips: {len(timeline.get('clips', []))}")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export and import DaVinci Resolve timelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export current timeline
  %(prog)s --export timeline_backup.json

  # Export with detailed clip information
  %(prog)s --export timeline_full.json --detailed

  # Import timeline
  %(prog)s --import timeline_backup.json

  # Show timeline info from export file
  %(prog)s --info timeline_backup.json
        """
    )

    # Actions
    action_group = parser.add_mutually_exclusive_group(required=True)

    action_group.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export current timeline to JSON file'
    )

    action_group.add_argument(
        '--import',
        dest='import_file',
        type=str,
        metavar='FILE',
        help='Import timeline from JSON file'
    )

    action_group.add_argument(
        '--info',
        type=str,
        metavar='FILE',
        help='Show timeline information from export file'
    )

    # Options
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed clip information in export'
    )

    args = parser.parse_args()

    # Show info without connecting to Resolve
    if args.info:
        try:
            with open(args.info, 'r') as f:
                export_data = json.load(f)

            print_timeline_info(export_data)
            return

        except FileNotFoundError:
            print(f"❌ File not found: {args.info}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)

    print("=" * 70)
    print("DaVinci Resolve Timeline Export/Import Tool")
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

    # Export timeline
    if args.export:
        timeline = project.GetCurrentTimeline()

        if not timeline:
            print("❌ No timeline is currently open")
            sys.exit(1)

        print(f"Exporting timeline: {timeline.GetName()}")
        print()

        export_data = export_timeline(timeline, detailed=args.detailed)

        try:
            with open(args.export, 'w') as f:
                json.dump(export_data, f, indent=2)

            file_size = os.path.getsize(args.export)
            print(f"✅ Timeline exported successfully")
            print(f"   File: {args.export}")
            print(f"   Size: {file_size} bytes")
            print(f"   Clips: {len(export_data['timeline']['clips'])}")
            print()

        except Exception as e:
            print(f"❌ Error writing export file: {e}")
            sys.exit(1)

    # Import timeline
    elif args.import_file:
        try:
            with open(args.import_file, 'r') as f:
                import_data = json.load(f)

        except FileNotFoundError:
            print(f"❌ File not found: {args.import_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON file: {e}")
            sys.exit(1)

        # Validate import data
        is_valid, error_msg = validate_import_data(import_data)
        if not is_valid:
            print(f"❌ Invalid import data: {error_msg}")
            sys.exit(1)

        print(f"Importing timeline from: {args.import_file}")
        print()

        # Show timeline info
        print_timeline_info(import_data)

        # Create timeline
        timeline = create_timeline_from_import(media_pool, import_data)

        if timeline:
            print()
            print("=" * 70)
            print("✅ Timeline imported successfully")
            print()
            print("Note: Clips are not automatically added.")
            print("      Timeline structure and settings have been created.")
            print("=" * 70)
        else:
            print()
            print("=" * 70)
            print("❌ Failed to import timeline")
            print("=" * 70)
            sys.exit(1)


if __name__ == "__main__":
    main()
