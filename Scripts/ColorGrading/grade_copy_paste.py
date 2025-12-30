#!/usr/bin/env python3
"""
Grade Copy/Paste Manager for DaVinci Resolve

Copy and paste color grading between clips with flexible options:
LUT-only, CDL-only, specific nodes, or complete grades.

Usage:
    # Copy grade from source clip to target clips
    python3 grade_copy_paste.py --source "ClipName" --target-track 1

    # Copy only LUTs
    python3 grade_copy_paste.py --source "ClipName" --target-all --luts-only

    # Copy specific node
    python3 grade_copy_paste.py --source "ClipName" --target-track 2 --node 4

    # Copy to clips with specific color
    python3 grade_copy_paste.py --source "ClipName" --target-color Orange

    # Save grade as template
    python3 grade_copy_paste.py --source "ClipName" --save-template my_grade.json

    # Apply template
    python3 grade_copy_paste.py --load-template my_grade.json --target-all

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import json
from typing import List, Dict, Optional, Any

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


def find_clip_in_timeline(timeline, clip_name: str) -> Optional[Any]:
    """
    Find clip by name in timeline.

    Args:
        timeline: Timeline object
        clip_name: Name of clip to find

    Returns:
        TimelineItem object or None
    """
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                if item.GetName() == clip_name:
                    return item

    return None


def get_target_clips(
    timeline,
    target_all: bool = False,
    target_track: Optional[int] = None,
    target_color: Optional[str] = None
) -> List[Any]:
    """
    Get target clips based on criteria.

    Args:
        timeline: Timeline object
        target_all: Target all clips
        target_track: Target specific track
        target_color: Target clips with specific color

    Returns:
        List of TimelineItem objects
    """
    clips = []
    video_track_count = timeline.GetTrackCount('video')

    for track_index in range(1, video_track_count + 1):
        # Skip if track filter doesn't match
        if target_track and track_index != target_track:
            continue

        items = timeline.GetItemListInTrack('video', track_index)
        if items:
            for item in items:
                # Apply color filter
                if target_color:
                    clip_color = item.GetClipColor()
                    if not clip_color or clip_color.lower() != target_color.lower():
                        continue

                clips.append(item)

    return clips


def extract_grade_info(clip, node: Optional[int] = None) -> Dict[str, Any]:
    """
    Extract grading information from clip.

    Args:
        clip: TimelineItem object
        node: Optional specific node to extract

    Returns:
        Dictionary with grade information
    """
    grade_info = {
        'clip_name': clip.GetName(),
        'node_count': 0,
        'nodes': []
    }

    try:
        node_count = clip.GetNumNodes()
        grade_info['node_count'] = node_count if node_count else 0
    except:
        grade_info['node_count'] = 0

    if grade_info['node_count'] == 0:
        return grade_info

    # Extract node information
    start_node = node if node else 1
    end_node = node if node else grade_info['node_count']

    for node_index in range(start_node, end_node + 1):
        if node_index > grade_info['node_count']:
            break

        node_info = {
            'index': node_index,
            'lut': None,
            'cdl': None
        }

        # Get LUT
        try:
            lut = clip.GetLUT(node_index)
            if lut and lut != "":
                node_info['lut'] = lut
        except:
            pass

        # Get CDL
        try:
            cdl = clip.GetNodeColorData(node_index)
            if cdl:
                node_info['cdl'] = cdl
        except:
            pass

        grade_info['nodes'].append(node_info)

    return grade_info


def copy_luts_only(source_clip, target_clip, node: Optional[int] = None) -> int:
    """
    Copy only LUTs from source to target.

    Args:
        source_clip: Source TimelineItem
        target_clip: Target TimelineItem
        node: Optional specific node

    Returns:
        Number of LUTs copied
    """
    copied = 0

    try:
        source_node_count = source_clip.GetNumNodes()
        target_node_count = target_clip.GetNumNodes()

        if not source_node_count or not target_node_count:
            return 0

        start_node = node if node else 1
        end_node = node if node else min(source_node_count, target_node_count)

        for node_index in range(start_node, end_node + 1):
            if node_index > source_node_count or node_index > target_node_count:
                break

            try:
                lut = source_clip.GetLUT(node_index)
                if lut and lut != "":
                    success = target_clip.SetLUT(node_index, lut)
                    if success:
                        copied += 1
            except:
                pass

    except:
        pass

    return copied


def copy_cdl_only(source_clip, target_clip, node: Optional[int] = None) -> int:
    """
    Copy only CDL from source to target.

    Args:
        source_clip: Source TimelineItem
        target_clip: Target TimelineItem
        node: Optional specific node

    Returns:
        Number of CDL copied
    """
    copied = 0

    try:
        source_node_count = source_clip.GetNumNodes()
        target_node_count = target_clip.GetNumNodes()

        if not source_node_count or not target_node_count:
            return 0

        start_node = node if node else 1
        end_node = node if node else min(source_node_count, target_node_count)

        for node_index in range(start_node, end_node + 1):
            if node_index > source_node_count or node_index > target_node_count:
                break

            try:
                cdl = source_clip.GetNodeColorData(node_index)
                if cdl:
                    success = target_clip.SetNodeColorData(node_index, cdl)
                    if success:
                        copied += 1
            except:
                pass

    except:
        pass

    return copied


def copy_complete_grade(source_clip, target_clip) -> bool:
    """
    Copy complete grade using built-in API.

    Args:
        source_clip: Source TimelineItem
        target_clip: Target TimelineItem

    Returns:
        True if successful
    """
    try:
        # Use CopyGrade/PasteGrade if available
        # Note: These methods may not be available in all API versions
        success = source_clip.CopyGrade()
        if success:
            success = target_clip.PasteGrade()
            return success
    except AttributeError:
        # Fallback: copy LUTs and CDL manually
        luts_copied = copy_luts_only(source_clip, target_clip)
        cdl_copied = copy_cdl_only(source_clip, target_clip)
        return (luts_copied > 0 or cdl_copied > 0)
    except:
        return False

    return False


def save_grade_template(clip, template_path: str, node: Optional[int] = None) -> bool:
    """
    Save grade information as JSON template.

    Args:
        clip: TimelineItem object
        template_path: Path to save template
        node: Optional specific node

    Returns:
        True if successful
    """
    try:
        grade_info = extract_grade_info(clip, node=node)

        with open(template_path, 'w') as f:
            json.dump(grade_info, f, indent=2)

        return True
    except Exception as e:
        print(f"❌ Error saving template: {e}")
        return False


def load_grade_template(template_path: str) -> Optional[Dict[str, Any]]:
    """
    Load grade template from JSON file.

    Args:
        template_path: Path to template file

    Returns:
        Grade information dictionary or None
    """
    try:
        with open(template_path, 'r') as f:
            grade_info = json.load(f)

        return grade_info
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return None


def apply_grade_template(clip, grade_info: Dict[str, Any]) -> bool:
    """
    Apply grade template to clip.

    Args:
        clip: TimelineItem object
        grade_info: Grade information dictionary

    Returns:
        True if successful
    """
    try:
        clip_node_count = clip.GetNumNodes()
        if not clip_node_count:
            return False

        applied = False

        for node_info in grade_info['nodes']:
            node_index = node_info['index']

            if node_index > clip_node_count:
                continue

            # Apply LUT
            if node_info['lut']:
                success = clip.SetLUT(node_index, node_info['lut'])
                if success:
                    applied = True

            # Apply CDL
            if node_info['cdl']:
                success = clip.SetNodeColorData(node_index, node_info['cdl'])
                if success:
                    applied = True

        return applied

    except Exception as e:
        print(f"❌ Error applying template: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Copy and paste color grades in DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Copy complete grade to all clips in track 1
  %(prog)s --source "MyClip" --target-track 1

  # Copy only LUTs to all clips
  %(prog)s --source "MyClip" --target-all --luts-only

  # Copy only CDL to all clips
  %(prog)s --source "MyClip" --target-all --cdl-only

  # Copy specific node to orange clips
  %(prog)s --source "MyClip" --target-color Orange --node 4

  # Save grade as template
  %(prog)s --source "MyClip" --save-template my_grade.json

  # Apply template to all clips
  %(prog)s --load-template my_grade.json --target-all

  # Dry run
  %(prog)s --source "MyClip" --target-all --dry-run
        """
    )

    # Source options
    source_group = parser.add_mutually_exclusive_group(required=True)

    source_group.add_argument(
        '--source',
        type=str,
        metavar='CLIP_NAME',
        help='Source clip name to copy grade from'
    )

    source_group.add_argument(
        '--load-template',
        type=str,
        metavar='FILE',
        help='Load grade from JSON template file'
    )

    # Target options
    target_group = parser.add_mutually_exclusive_group()

    target_group.add_argument(
        '--target-all',
        action='store_true',
        help='Apply to all clips in timeline'
    )

    target_group.add_argument(
        '--target-track',
        type=int,
        metavar='N',
        help='Apply to clips in specific track'
    )

    target_group.add_argument(
        '--target-color',
        type=str,
        metavar='COLOR',
        help='Apply to clips with specific color'
    )

    # Copy options
    copy_mode = parser.add_mutually_exclusive_group()

    copy_mode.add_argument(
        '--luts-only',
        action='store_true',
        help='Copy only LUTs'
    )

    copy_mode.add_argument(
        '--cdl-only',
        action='store_true',
        help='Copy only CDL values'
    )

    # Node selection
    parser.add_argument(
        '--node',
        type=int,
        metavar='N',
        help='Copy specific node only'
    )

    # Template saving
    parser.add_argument(
        '--save-template',
        type=str,
        metavar='FILE',
        help='Save grade as JSON template'
    )

    # Other options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without applying'
    )

    args = parser.parse_args()

    # Validation
    if args.source and args.save_template and not (args.target_all or args.target_track or args.target_color):
        # Allow save-template without targets
        pass
    elif args.source and not (args.target_all or args.target_track or args.target_color) and not args.save_template:
        print("Error: Specify target (--target-all, --target-track, or --target-color)")
        sys.exit(1)
    elif args.load_template and not (args.target_all or args.target_track or args.target_color):
        print("Error: Specify target (--target-all, --target-track, or --target-color)")
        sys.exit(1)

    print("=" * 70)
    print("DaVinci Resolve Grade Copy/Paste Manager")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No grades will be applied")
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

    # Handle template save
    if args.source and args.save_template:
        source_clip = find_clip_in_timeline(timeline, args.source)

        if not source_clip:
            print(f"❌ Source clip not found: {args.source}")
            sys.exit(1)

        print(f"Saving grade from: {args.source}")
        success = save_grade_template(source_clip, args.save_template, node=args.node)

        if success:
            print(f"✅ Template saved: {args.save_template}")
        else:
            print(f"❌ Failed to save template")

        sys.exit(0 if success else 1)

    # Get source grade
    if args.source:
        source_clip = find_clip_in_timeline(timeline, args.source)

        if not source_clip:
            print(f"❌ Source clip not found: {args.source}")
            sys.exit(1)

        print(f"Source clip: {args.source}")
        grade_template = None

    elif args.load_template:
        grade_template = load_grade_template(args.load_template)

        if not grade_template:
            print(f"❌ Failed to load template: {args.load_template}")
            sys.exit(1)

        print(f"Loaded template: {args.load_template}")
        print(f"  Source: {grade_template['clip_name']}")
        print(f"  Nodes: {len(grade_template['nodes'])}")
        source_clip = None

    print()

    # Get target clips
    target_clips = get_target_clips(
        timeline,
        target_all=args.target_all,
        target_track=args.target_track,
        target_color=args.target_color
    )

    if not target_clips:
        print("❌ No target clips found")
        sys.exit(1)

    print(f"Found {len(target_clips)} target clip(s)")
    print()

    # Apply grade
    print("Applying grade...")
    print()

    applied = 0

    for target_clip in target_clips:
        target_name = target_clip.GetName()

        # Skip source clip
        if source_clip and target_clip == source_clip:
            print(f"  ⚠️  Skipped (source): {target_name}")
            continue

        if args.dry_run:
            print(f"  Would apply to: {target_name}")
            applied += 1
            continue

        success = False

        if source_clip:
            if args.luts_only:
                copied = copy_luts_only(source_clip, target_clip, node=args.node)
                success = (copied > 0)
            elif args.cdl_only:
                copied = copy_cdl_only(source_clip, target_clip, node=args.node)
                success = (copied > 0)
            elif args.node:
                luts = copy_luts_only(source_clip, target_clip, node=args.node)
                cdl = copy_cdl_only(source_clip, target_clip, node=args.node)
                success = (luts > 0 or cdl > 0)
            else:
                success = copy_complete_grade(source_clip, target_clip)

        elif grade_template:
            success = apply_grade_template(target_clip, grade_template)

        if success:
            print(f"  ✅ Applied to: {target_name}")
            applied += 1
        else:
            print(f"  ❌ Failed: {target_name}")

    # Summary
    print()
    print("=" * 70)

    if args.dry_run:
        print(f"Would apply grade to {applied} clip(s)")
    else:
        print(f"✅ Applied grade to {applied} clip(s)")

    print("=" * 70)


if __name__ == "__main__":
    main()
