#!/usr/bin/env python3
"""
Batch Text/Title Generator for DaVinci Resolve

Generate text overlays and titles based on clip metadata, templates,
and custom text lists. Useful for creating slates, lower thirds, credits.

Usage:
    # Generate slates from clip metadata
    python3 batch_text_title_generator.py --slate --all

    # Create lower thirds from CSV
    python3 batch_text_title_generator.py --lower-third --source names.csv

    # Generate timecode burn-in guide
    python3 batch_text_title_generator.py --timecode-guide

    # Create custom text overlays
    python3 batch_text_title_generator.py --custom "My Text" --track 1

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


# Text templates
TEXT_TEMPLATES = {
    'slate': {
        'name': 'Production Slate',
        'fields': ['Scene', 'Shot', 'Take', 'Camera', 'Date'],
        'description': 'Standard production slate with scene/shot info'
    },
    'lower_third': {
        'name': 'Lower Third',
        'fields': ['Name', 'Title'],
        'description': 'Interview lower third with name and title'
    },
    'title_card': {
        'name': 'Title Card',
        'fields': ['Title', 'Subtitle'],
        'description': 'Opening/closing title card'
    },
    'watermark': {
        'name': 'Watermark',
        'fields': ['Text'],
        'description': 'Simple text watermark overlay'
    },
    'timecode': {
        'name': 'Timecode Overlay',
        'fields': ['Timecode', 'Frame'],
        'description': 'Timecode and frame number display'
    },
}


def get_target_clips(
    timeline,
    target_all: bool = False,
    target_track: Optional[int] = None,
    target_color: Optional[str] = None
) -> List[Any]:
    """Get target clips based on criteria."""
    clips = []
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        if target_track and track_index != target_track:
            continue

        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                if target_color:
                    clip_color = item.GetClipColor()
                    if not clip_color or clip_color.lower() != target_color.lower():
                        continue
                clips.append(item)

    return clips


def load_text_from_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Load text data from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of dictionaries with text data
    """
    text_data = []

    try:
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                text_data.append(dict(row))

        return text_data

    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []


def generate_slate_text(clip) -> str:
    """
    Generate slate text from clip metadata.

    Args:
        clip: TimelineItem object

    Returns:
        Formatted slate text
    """
    text_parts = []

    # Get clip name
    clip_name = clip.GetName()
    text_parts.append(f"Clip: {clip_name}")

    # Try to get metadata
    try:
        metadata = clip.GetMetadata()

        if isinstance(metadata, dict):
            # TimelineItem API
            scene = metadata.get('Scene', '')
            shot = metadata.get('Shot', '')
            take = metadata.get('Take', '')

            if scene:
                text_parts.append(f"Scene: {scene}")
            if shot:
                text_parts.append(f"Shot: {shot}")
            if take:
                text_parts.append(f"Take: {take}")
        else:
            # Try MediaPoolItem API
            try:
                scene = clip.GetMetadata('Scene') or ''
                shot = clip.GetMetadata('Shot') or ''
                take = clip.GetMetadata('Take') or ''

                if scene:
                    text_parts.append(f"Scene: {scene}")
                if shot:
                    text_parts.append(f"Shot: {shot}")
                if take:
                    text_parts.append(f"Take: {take}")
            except:
                pass

    except:
        pass

    # Get timing info
    duration = clip.GetDuration()
    text_parts.append(f"Duration: {duration} frames")

    return " | ".join(text_parts)


def show_text_generation_guide(template: str) -> None:
    """
    Show guide for generating text/titles.

    Args:
        template: Template name
    """
    print("=" * 70)
    print(f"Text/Title Generation Guide: {template}")
    print("=" * 70)
    print()

    if template == 'slate':
        print("Production Slate Setup:")
        print()
        print("1. Create Text+ node in Fusion page:")
        print("   • Switch to Fusion page")
        print("   • Select clip where you want slate")
        print("   • Add Text+ node from Effects Library")
        print()
        print("2. Configure text:")
        print("   • Set font, size, and color")
        print("   • Position at top or bottom")
        print("   • Add background rectangle (optional)")
        print()
        print("3. Use metadata for dynamic text:")
        print("   • Scene: [Scene]")
        print("   • Shot: [Shot]")
        print("   • Take: [Take]")
        print("   • Camera: [Camera]")
        print()

    elif template == 'lower_third':
        print("Lower Third Setup:")
        print()
        print("1. Create Fusion Composition:")
        print("   • Effects Library → Titles → Lower 3rd")
        print("   • Or create custom Text+ composition")
        print()
        print("2. Design elements:")
        print("   • Name text (larger font)")
        print("   • Title/Description (smaller font)")
        print("   • Background shape/bar")
        print("   • Optional logo")
        print()
        print("3. Animation:")
        print("   • Add keyframes for slide-in/out")
        print("   • Typical duration: 3-5 seconds")
        print()
        print("4. Apply to clips:")
        print("   • Drag to timeline above interview clips")
        print("   • Adjust timing as needed")
        print()

    elif template == 'timecode':
        print("Timecode Overlay Setup:")
        print()
        print("1. Fusion Text+ method:")
        print("   • Add Text+ node")
        print("   • Use expression: Text = Comp:GetAttrs().COMPN_RenderStart")
        print("   • Or use frame counter: Text = time")
        print()
        print("2. Built-in method (easier):")
        print("   • Right-click on clip")
        print("   • Select 'Burn In'")
        print("   • Choose burn-in options:")
        print("     - Timecode")
        print("     - Clip name")
        print("     - Frame number")
        print()
        print("3. Position:")
        print("   • Top-left for technical review")
        print("   • Bottom for broadcast safe")
        print()

    elif template == 'watermark':
        print("Watermark Setup:")
        print()
        print("1. Create semi-transparent text:")
        print("   • Add Text+ node in Fusion")
        print("   • Set text to your watermark")
        print("   • Reduce opacity to 20-40%")
        print()
        print("2. Position:")
        print("   • Bottom-right corner (most common)")
        print("   • Or center for protection")
        print()
        print("3. Apply to all clips:")
        print("   • Create as Adjustment Clip")
        print("   • Place on top video track")
        print("   • Spans entire timeline")
        print()

    elif template == 'title_card':
        print("Title Card Setup:")
        print()
        print("1. Create title generator:")
        print("   • Effects Library → Titles")
        print("   • Choose template or create custom")
        print()
        print("2. Common title types:")
        print("   • Opening title (film/episode name)")
        print("   • Chapter/section titles")
        print("   • End credits")
        print()
        print("3. Animation:")
        print("   • Fade in/out")
        print("   • Slide up/down")
        print("   • Credits scroll")
        print()
        print("4. Duration:")
        print("   • Opening: 3-5 seconds")
        print("   • Chapter: 2-3 seconds")
        print("   • End credits: 30-60 seconds")
        print()

    print("=" * 70)
    print()
    print("Note: DaVinci Resolve API has limited text/title generation support.")
    print("Most text operations require manual creation in Fusion or Edit page.")
    print()
    print("For batch operations:")
    print("  1. Create template title/text in Fusion")
    print("  2. Save as Power Bin or Compound Clip")
    print("  3. Duplicate and modify for each instance")
    print("=" * 70)


def analyze_clips_for_text(clips: List[Any]) -> Dict[str, Any]:
    """
    Analyze clips to suggest text overlay opportunities.

    Args:
        clips: List of clips

    Returns:
        Dictionary with suggestions
    """
    suggestions = {
        'needs_slate': [],
        'needs_lower_third': [],
        'has_metadata': [],
        'unnamed': [],
    }

    for clip in clips:
        clip_name = clip.GetName()

        # Check metadata
        has_metadata = False
        try:
            metadata = clip.GetMetadata()
            if isinstance(metadata, dict):
                if any(metadata.get(field) for field in ['Scene', 'Shot', 'Take']):
                    has_metadata = True
                    suggestions['has_metadata'].append(clip)
        except:
            pass

        # Check for unnamed clips
        if clip_name.startswith('Untitled') or not clip_name:
            suggestions['unnamed'].append(clip)

        # Heuristics for text needs
        name_lower = clip_name.lower()

        if 'interview' in name_lower or 'talking_head' in name_lower:
            suggestions['needs_lower_third'].append(clip)

        if has_metadata:
            suggestions['needs_slate'].append(clip)

    return suggestions


def export_text_template(template: str, output_path: str) -> bool:
    """
    Export text template as CSV for batch processing.

    Args:
        template: Template name
        output_path: Output CSV path

    Returns:
        True if successful
    """
    try:
        if template not in TEXT_TEMPLATES:
            return False

        template_info = TEXT_TEMPLATES[template]
        fields = template_info['fields']

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            # Write example rows
            if template == 'slate':
                writer.writerow({
                    'Scene': '001',
                    'Shot': 'A',
                    'Take': '1',
                    'Camera': 'CAM1',
                    'Date': '2024-01-01'
                })
            elif template == 'lower_third':
                writer.writerow({
                    'Name': 'John Doe',
                    'Title': 'Director of Photography'
                })
            elif template == 'title_card':
                writer.writerow({
                    'Title': 'Episode One',
                    'Subtitle': 'The Beginning'
                })

        return True

    except Exception as e:
        print(f"Error exporting template: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch text/title generator for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show slate generation guide
  %(prog)s --guide slate

  # Show lower third guide
  %(prog)s --guide lower_third

  # Show timecode overlay guide
  %(prog)s --guide timecode

  # Analyze clips for text opportunities
  %(prog)s --analyze --all

  # Export template CSV
  %(prog)s --export-template lower_third --output names.csv

  # List available templates
  %(prog)s --list-templates

Note:
  DaVinci Resolve API has limited text/title generation capabilities.
  This tool provides workflow guidance and batch planning assistance.
  Actual text creation requires Fusion page or Edit page title tools.

Available templates: slate, lower_third, title_card, watermark, timecode
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--guide',
        type=str,
        choices=list(TEXT_TEMPLATES.keys()),
        help='Show text generation guide for template'
    )

    mode_group.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze clips and suggest text overlay opportunities'
    )

    mode_group.add_argument(
        '--export-template',
        type=str,
        choices=list(TEXT_TEMPLATES.keys()),
        help='Export text template as CSV'
    )

    mode_group.add_argument(
        '--list-templates',
        action='store_true',
        help='List available text templates'
    )

    mode_group.add_argument(
        '--show-slate-data',
        action='store_true',
        help='Show slate data from clip metadata'
    )

    # Target selection (for analyze and show-slate-data)
    target_group = parser.add_mutually_exclusive_group()

    target_group.add_argument(
        '--all',
        action='store_true',
        help='Apply to all clips in timeline'
    )

    target_group.add_argument(
        '--track',
        type=int,
        metavar='N',
        help='Apply to clips in specific track'
    )

    target_group.add_argument(
        '--color',
        type=str,
        metavar='COLOR',
        help='Apply to clips with specific color'
    )

    # Output file
    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Output file path'
    )

    args = parser.parse_args()

    # List templates
    if args.list_templates:
        print("=" * 70)
        print("Available Text/Title Templates")
        print("=" * 70)
        print()

        for key, template in TEXT_TEMPLATES.items():
            print(f"{key}:")
            print(f"  {template['name']}")
            print(f"  {template['description']}")
            print(f"  Fields: {', '.join(template['fields'])}")
            print()

        return

    # Show guide
    if args.guide:
        show_text_generation_guide(args.guide)
        return

    # Export template
    if args.export_template:
        if not args.output:
            print("Error: --export-template requires --output")
            sys.exit(1)

        print(f"Exporting template: {args.export_template}")
        print(f"Output: {args.output}")
        print()

        success = export_text_template(args.export_template, args.output)

        if success:
            print(f"✅ Successfully exported template to: {args.output}")
            print()
            print("Edit the CSV file with your text data, then use it for")
            print("batch text generation in your video editing workflow.")
        else:
            print("❌ Export failed")

        return

    print("=" * 70)
    print("DaVinci Resolve Batch Text/Title Generator")
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

        if not timeline and (args.analyze or args.show_slate_data):
            print("❌ No timeline is currently open")
            sys.exit(1)

        print(f"✅ Connected to project: {project.GetName()}")
        if timeline:
            print(f"✅ Timeline: {timeline.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Analyze or show slate data
    if args.analyze or args.show_slate_data:
        if not args.all and not args.track and not args.color:
            print("Error: Specify target (--all, --track, or --color)")
            sys.exit(1)

        target_clips = get_target_clips(
            timeline,
            target_all=args.all,
            target_track=args.track,
            target_color=args.color
        )

        if not target_clips:
            print("❌ No target clips found")
            sys.exit(1)

        print(f"Found {len(target_clips)} target clip(s)")
        print()

        if args.analyze:
            print("Analyzing clips for text overlay opportunities...")
            print()

            suggestions = analyze_clips_for_text(target_clips)

            if suggestions['needs_slate']:
                print(f"📋 Clips with metadata (good for slates): {len(suggestions['needs_slate'])}")
                for clip in suggestions['needs_slate'][:5]:  # Show first 5
                    print(f"   • {clip.GetName()}")
                if len(suggestions['needs_slate']) > 5:
                    print(f"   ... and {len(suggestions['needs_slate']) - 5} more")
                print()

            if suggestions['needs_lower_third']:
                print(f"🎤 Clips needing lower thirds: {len(suggestions['needs_lower_third'])}")
                for clip in suggestions['needs_lower_third']:
                    print(f"   • {clip.GetName()}")
                print()

            if suggestions['unnamed']:
                print(f"⚠️  Unnamed clips: {len(suggestions['unnamed'])}")
                for clip in suggestions['unnamed'][:5]:
                    print(f"   • {clip.GetName()}")
                if len(suggestions['unnamed']) > 5:
                    print(f"   ... and {len(suggestions['unnamed']) - 5} more")
                print()

        elif args.show_slate_data:
            print("Slate Data from Clip Metadata:")
            print()

            for clip in target_clips:
                slate_text = generate_slate_text(clip)
                print(f"📹 {slate_text}")
                print()

    print("=" * 70)


if __name__ == "__main__":
    main()
