#!/usr/bin/env python3
"""
Metadata Manager for DaVinci Resolve

Bulk manage, edit, import, and export metadata for media pool clips
and timeline items.

Usage:
    # List all metadata
    python3 metadata_manager.py --list

    # Export metadata to CSV
    python3 metadata_manager.py --export metadata.csv

    # Import metadata from CSV
    python3 metadata_manager.py --import metadata.csv

    # Set metadata field
    python3 metadata_manager.py --set-field "Scene" "101A" --search "interview"

    # Find clips by metadata
    python3 metadata_manager.py --find-by "Scene=101"

    # Work with timeline clips
    python3 metadata_manager.py --timeline --list

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import csv
import json
import argparse
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Common metadata fields
METADATA_FIELDS = [
    'Clip Name',
    'Scene',
    'Shot',
    'Take',
    'Angle',
    'Camera',
    'Keywords',
    'Description',
    'Comments',
    'Good Take',
    'Reel Name'
]


def get_all_clips_from_media_pool(media_pool) -> List[Tuple[Any, str]]:
    """
    Get all clips from media pool recursively.

    Args:
        media_pool: MediaPool object

    Returns:
        List of (clip, folder_path) tuples
    """
    clips = []

    def traverse_folder(folder, path: str = ""):
        """Recursive traversal helper."""
        folder_name = folder.GetName()
        current_path = f"{path}/{folder_name}" if path else folder_name

        # Get clips in current folder
        folder_clips = folder.GetClipList()
        if folder_clips:
            for clip in folder_clips:
                clips.append((clip, current_path))

        # Recurse into subfolders
        subfolders = folder.GetSubFolderList()
        if subfolders:
            for subfolder in subfolders:
                traverse_folder(subfolder, current_path)

    root_folder = media_pool.GetRootFolder()
    traverse_folder(root_folder)

    return clips


def get_clips_from_timeline(timeline) -> List[Any]:
    """
    Get all clips from timeline.

    Args:
        timeline: Timeline object

    Returns:
        List of TimelineItem objects
    """
    clips = []
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            clips.extend(items)

    return clips


def get_clip_metadata(clip, include_properties: bool = False) -> Dict[str, Any]:
    """
    Get metadata from clip.

    Args:
        clip: MediaPoolItem or TimelineItem object
        include_properties: Include clip properties (resolution, codec, etc.)

    Returns:
        Dictionary with metadata
    """
    metadata = {
        'name': clip.GetName(),
        'metadata': {}
    }

    # Get metadata fields
    # Note: TimelineItem.GetMetadata() returns dict, MediaPoolItem.GetMetadata(field) returns string
    try:
        # Try TimelineItem API first (returns dict)
        metadata_dict = clip.GetMetadata()
        if isinstance(metadata_dict, dict):
            for field in METADATA_FIELDS:
                value = metadata_dict.get(field)
                if value:
                    metadata['metadata'][field] = value
        else:
            # MediaPoolItem API (takes field parameter)
            for field in METADATA_FIELDS:
                value = clip.GetMetadata(field)
                if value:
                    metadata['metadata'][field] = value
    except TypeError:
        # Fallback for MediaPoolItem
        for field in METADATA_FIELDS:
            try:
                value = clip.GetMetadata(field)
                if value:
                    metadata['metadata'][field] = value
            except:
                pass

    # Optionally include properties
    if include_properties:
        try:
            props = clip.GetClipProperty()
            if props:
                metadata['properties'] = {
                    'resolution': f"{props.get('Width', '')}x{props.get('Height', '')}",
                    'fps': props.get('FPS', ''),
                    'codec': props.get('Video Codec', ''),
                    'duration': props.get('Duration', ''),
                    'file_path': props.get('File Path', '')
                }
        except:
            pass

    return metadata


def set_clip_metadata(clip, field: str, value: str) -> bool:
    """
    Set metadata field on clip.

    Args:
        clip: MediaPoolItem or TimelineItem object
        field: Metadata field name
        value: Value to set

    Returns:
        True if successful
    """
    try:
        # TimelineItem.SetMetadata() takes a dict
        # MediaPoolItem.SetMetadata() takes field and value
        # Try dict approach first (TimelineItem)
        result = clip.SetMetadata({field: value})
        if result is not None:
            return result
        # Fallback to field/value approach (MediaPoolItem)
        return clip.SetMetadata(field, value)
    except Exception as e:
        # Try the other API
        try:
            return clip.SetMetadata(field, value)
        except:
            print(f"  ❌ Error setting metadata: {e}")
            return False


def list_metadata(clips: List, show_properties: bool = False):
    """
    List metadata for clips.

    Args:
        clips: List of clips or (clip, path) tuples
        show_properties: Include clip properties
    """
    print("=" * 70)
    print("Clip Metadata")
    print("=" * 70)
    print()

    if not clips:
        print("No clips found")
        return

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
            print(f"📁 Location: {path}")
        else:
            clip = item

        metadata = get_clip_metadata(clip, include_properties=show_properties)

        print(f"🎬 {metadata['name']}")

        if metadata['metadata']:
            for field, value in metadata['metadata'].items():
                print(f"   {field}: {value}")
        else:
            print("   (No metadata)")

        if show_properties and 'properties' in metadata:
            print(f"   ---")
            for prop, value in metadata['properties'].items():
                if value:
                    print(f"   {prop}: {value}")

        print()

    print("=" * 70)


def export_metadata_csv(clips: List, output_file: str, include_properties: bool = False):
    """
    Export metadata to CSV file.

    Args:
        clips: List of clips or (clip, path) tuples
        output_file: Output CSV file path
        include_properties: Include clip properties
    """
    if not clips:
        print("No clips to export")
        return

    print(f"Exporting metadata to: {output_file}")
    print()

    # Prepare CSV headers
    headers = ['Clip Name', 'Location'] + METADATA_FIELDS

    if include_properties:
        headers.extend(['Resolution', 'FPS', 'Codec', 'Duration', 'File Path'])

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for item in clips:
            # Handle both clip objects and (clip, path) tuples
            if isinstance(item, tuple):
                clip, path = item
            else:
                clip = item
                path = ""

            metadata = get_clip_metadata(clip, include_properties=include_properties)

            row = {
                'Clip Name': metadata['name'],
                'Location': path
            }

            # Add metadata fields
            for field in METADATA_FIELDS:
                row[field] = metadata['metadata'].get(field, '')

            # Add properties if requested
            if include_properties and 'properties' in metadata:
                row['Resolution'] = metadata['properties'].get('resolution', '')
                row['FPS'] = metadata['properties'].get('fps', '')
                row['Codec'] = metadata['properties'].get('codec', '')
                row['Duration'] = metadata['properties'].get('duration', '')
                row['File Path'] = metadata['properties'].get('file_path', '')

            writer.writerow(row)

    print(f"✅ Exported {len(clips)} clip(s)")


def export_metadata_json(clips: List, output_file: str, include_properties: bool = False):
    """
    Export metadata to JSON file.

    Args:
        clips: List of clips or (clip, path) tuples
        output_file: Output JSON file path
        include_properties: Include clip properties
    """
    if not clips:
        print("No clips to export")
        return

    print(f"Exporting metadata to: {output_file}")
    print()

    export_data = []

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item
            path = ""

        metadata = get_clip_metadata(clip, include_properties=include_properties)
        metadata['location'] = path
        export_data.append(metadata)

    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

    print(f"✅ Exported {len(clips)} clip(s)")


def import_metadata_csv(clips: List, input_file: str, dry_run: bool = False) -> int:
    """
    Import metadata from CSV file.

    Args:
        clips: List of clips or (clip, path) tuples
        input_file: Input CSV file path
        dry_run: If True, only show what would be done

    Returns:
        Number of clips updated
    """
    if not os.path.isfile(input_file):
        print(f"❌ File not found: {input_file}")
        return 0

    print(f"Importing metadata from: {input_file}")
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    # Build clip lookup dictionary
    clip_dict = {}
    for item in clips:
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item

        clip_dict[clip.GetName()] = clip

    updated_count = 0

    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            clip_name = row.get('Clip Name', '')

            if not clip_name:
                continue

            clip = clip_dict.get(clip_name)

            if not clip:
                print(f"⚠️  Clip not found: {clip_name}")
                continue

            print(f"🎬 {clip_name}")

            # Update metadata fields
            fields_updated = False

            for field in METADATA_FIELDS:
                value = row.get(field, '').strip()

                if value:
                    print(f"   {field}: {value}")

                    if not dry_run:
                        if set_clip_metadata(clip, field, value):
                            fields_updated = True
                        else:
                            print(f"   ⚠️  Failed to set {field}")

            if fields_updated or dry_run:
                updated_count += 1

            print()

    return updated_count


def set_metadata_bulk(clips: List, field: str, value: str, dry_run: bool = False) -> int:
    """
    Set metadata field on multiple clips.

    Args:
        clips: List of clips or (clip, path) tuples
        field: Metadata field name
        value: Value to set
        dry_run: If True, only show what would be done

    Returns:
        Number of clips updated
    """
    if not clips:
        print("No clips to update")
        return 0

    print(f"Setting '{field}' = '{value}' on {len(clips)} clip(s)")
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print()

    updated_count = 0

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item

        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would update: {clip_name}")
            updated_count += 1
        else:
            if set_clip_metadata(clip, field, value):
                print(f"  ✅ Updated: {clip_name}")
                updated_count += 1
            else:
                print(f"  ❌ Failed: {clip_name}")

    return updated_count


def find_by_metadata(clips: List, search_field: str, search_value: str) -> List:
    """
    Find clips by metadata value.

    Args:
        clips: List of clips or (clip, path) tuples
        search_field: Metadata field to search
        search_value: Value to search for

    Returns:
        List of matching clips
    """
    matches = []

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item

        value = clip.GetMetadata(search_field)

        if value and search_value.lower() in value.lower():
            matches.append(item)

    return matches


def search_clips_by_name(clips: List, query: str) -> List:
    """
    Search clips by name.

    Args:
        clips: List of clips or (clip, path) tuples
        query: Search query

    Returns:
        List of matching clips
    """
    matches = []

    for item in clips:
        # Handle both clip objects and (clip, path) tuples
        if isinstance(item, tuple):
            clip, path = item
        else:
            clip = item

        if query.lower() in clip.GetName().lower():
            matches.append(item)

    return matches


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage metadata for DaVinci Resolve clips",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List metadata for all media pool clips
  %(prog)s --list

  # List with properties
  %(prog)s --list --properties

  # Export to CSV
  %(prog)s --export metadata.csv

  # Export to JSON
  %(prog)s --export metadata.json --properties

  # Import from CSV
  %(prog)s --import metadata.csv

  # Set metadata on clips matching search
  %(prog)s --set-field "Scene" "101A" --search "interview"

  # Find clips by metadata
  %(prog)s --find-by "Scene=101"

  # Work with timeline clips
  %(prog)s --timeline --list
  %(prog)s --timeline --set-field "Status" "Approved"
        """
    )

    # Source selection
    parser.add_argument(
        '--timeline',
        action='store_true',
        help='Work with timeline clips instead of media pool'
    )

    # Actions
    parser.add_argument(
        '--list',
        action='store_true',
        help='List metadata for all clips'
    )

    parser.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export metadata to CSV or JSON file'
    )

    parser.add_argument(
        '--import',
        dest='import_file',
        type=str,
        metavar='FILE',
        help='Import metadata from CSV file'
    )

    parser.add_argument(
        '--set-field',
        nargs=2,
        metavar=('FIELD', 'VALUE'),
        help='Set metadata field to value'
    )

    parser.add_argument(
        '--find-by',
        type=str,
        metavar='FIELD=VALUE',
        help='Find clips by metadata (format: Field=Value)'
    )

    # Options
    parser.add_argument(
        '--search',
        type=str,
        metavar='QUERY',
        help='Filter clips by name (use with --set-field)'
    )

    parser.add_argument(
        '--properties',
        action='store_true',
        help='Include clip properties in output'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Need at least one action
    if not any([args.list, args.export, args.import_file, args.set_field, args.find_by]):
        parser.print_help()
        return

    print("=" * 70)
    print("DaVinci Resolve Metadata Manager")
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

    # Get clips
    if args.timeline:
        timeline = project.GetCurrentTimeline()

        if not timeline:
            print("❌ No timeline is currently open")
            sys.exit(1)

        print(f"Working with timeline: {timeline.GetName()}")
        clips = get_clips_from_timeline(timeline)
        print(f"Found {len(clips)} clip(s) in timeline")
    else:
        media_pool = project.GetMediaPool()

        if not media_pool:
            print("❌ Could not access media pool")
            sys.exit(1)

        print("Working with media pool")
        clips = get_all_clips_from_media_pool(media_pool)
        print(f"Found {len(clips)} clip(s) in media pool")

    print()

    # Apply search filter if specified
    if args.search:
        print(f"Filtering by name: {args.search}")
        clips = search_clips_by_name(clips, args.search)
        print(f"Filtered to {len(clips)} clip(s)")
        print()

    # Execute actions
    if args.list:
        list_metadata(clips, show_properties=args.properties)

    if args.export:
        output_file = args.export

        if output_file.endswith('.json'):
            export_metadata_json(clips, output_file, include_properties=args.properties)
        else:
            export_metadata_csv(clips, output_file, include_properties=args.properties)

        print()

    if args.import_file:
        updated = import_metadata_csv(clips, args.import_file, dry_run=args.dry_run)
        print("=" * 70)

        if args.dry_run:
            print(f"Would update {updated} clip(s)")
        else:
            print(f"✅ Updated {updated} clip(s)")

        print("=" * 70)

    if args.set_field:
        field, value = args.set_field
        updated = set_metadata_bulk(clips, field, value, dry_run=args.dry_run)

        print()
        print("=" * 70)

        if args.dry_run:
            print(f"Would update {updated} clip(s)")
        else:
            print(f"✅ Updated {updated} clip(s)")

        print("=" * 70)

    if args.find_by:
        # Parse Field=Value
        if '=' not in args.find_by:
            print("❌ --find-by format must be: Field=Value")
            sys.exit(1)

        field, value = args.find_by.split('=', 1)
        matches = find_by_metadata(clips, field, value)

        print("=" * 70)
        print(f"Search Results: {field} = {value}")
        print("=" * 70)
        print()

        if matches:
            print(f"Found {len(matches)} match(es):")
            print()

            for item in matches:
                if isinstance(item, tuple):
                    clip, path = item
                    print(f"🎬 {clip.GetName()}")
                    print(f"   Location: {path}")
                else:
                    clip = item
                    print(f"🎬 {clip.GetName()}")

                print()
        else:
            print("No matches found")

        print("=" * 70)


if __name__ == "__main__":
    main()
