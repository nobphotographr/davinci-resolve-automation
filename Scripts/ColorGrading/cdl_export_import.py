#!/usr/bin/env python3
"""
CDL Export/Import Tool for DaVinci Resolve

Export and import ASC CDL (Color Decision List) files for color grading
interchange with other applications like Baselight, Nuke, and Adobe apps.

CDL Format:
    - Slope (gain/highlights)
    - Offset (lift/shadows)
    - Power (gamma/midtones)
    - Saturation

Usage:
    # Export CDL from all clips
    python3 cdl_export_import.py --export output.cdl --all

    # Export CDL from specific track
    python3 cdl_export_import.py --export grades.cdl --track 1

    # Import CDL to clips
    python3 cdl_export_import.py --import input.cdl --all

    # Export single clip
    python3 cdl_export_import.py --export clip.cdl --color Orange

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


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


def get_cdl_from_clip(clip, node_index: int = 1) -> Optional[Dict[str, Any]]:
    """
    Get CDL data from clip.

    Args:
        clip: TimelineItem object
        node_index: Node index to read from

    Returns:
        CDL dictionary or None
    """
    try:
        cdl = clip.GetNodeColorData(node_index)
        if cdl:
            return cdl
        else:
            # Return default CDL if none exists
            return {
                'slope': [1.0, 1.0, 1.0, 1.0],
                'offset': [0.0, 0.0, 0.0, 0.0],
                'power': [1.0, 1.0, 1.0, 1.0],
                'saturation': 1.0
            }
    except:
        return None


def set_cdl_to_clip(clip, cdl: Dict[str, Any], node_index: int = 1) -> bool:
    """
    Set CDL data to clip.

    Args:
        clip: TimelineItem object
        cdl: CDL dictionary
        node_index: Node index to write to

    Returns:
        True if successful
    """
    try:
        return clip.SetNodeColorData(node_index, cdl)
    except:
        return False


def export_cdl_xml(clips: List[Any], output_path: str, timeline_name: str = "Timeline") -> bool:
    """
    Export CDL data to ASC CDL XML file.

    Args:
        clips: List of clips
        output_path: Output file path
        timeline_name: Timeline name for metadata

    Returns:
        True if successful
    """
    try:
        # Create root element
        root = ET.Element('ColorDecisionList', {
            'xmlns': 'urn:ASC:CDL:v1.2'
        })

        # Add metadata
        description = ET.SubElement(root, 'Description')
        description.text = f'Exported from DaVinci Resolve - {timeline_name}'

        input_desc = ET.SubElement(root, 'InputDescription')
        input_desc.text = f'Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        viewer_desc = ET.SubElement(root, 'ViewingDescription')
        viewer_desc.text = 'DaVinci Resolve Color Grading'

        # Add ColorCorrections
        for clip in clips:
            clip_name = clip.GetName()
            cdl = get_cdl_from_clip(clip)

            if not cdl:
                continue

            # Create ColorCorrection element
            cc = ET.SubElement(root, 'ColorCorrection', {'id': clip_name})

            # Add SOPNode (Slope, Offset, Power)
            sop_node = ET.SubElement(cc, 'SOPNode')

            slope = ET.SubElement(sop_node, 'Slope')
            slope.text = f"{cdl['slope'][0]:.6f} {cdl['slope'][1]:.6f} {cdl['slope'][2]:.6f}"

            offset = ET.SubElement(sop_node, 'Offset')
            offset.text = f"{cdl['offset'][0]:.6f} {cdl['offset'][1]:.6f} {cdl['offset'][2]:.6f}"

            power = ET.SubElement(sop_node, 'Power')
            power.text = f"{cdl['power'][0]:.6f} {cdl['power'][1]:.6f} {cdl['power'][2]:.6f}"

            # Add SatNode
            sat_node = ET.SubElement(cc, 'SatNode')
            saturation = ET.SubElement(sat_node, 'Saturation')
            saturation.text = f"{cdl['saturation']:.6f}"

        # Pretty print XML
        xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')

        # Write to file
        with open(output_path, 'w') as f:
            f.write(xml_string)

        return True

    except Exception as e:
        print(f"Error exporting CDL: {e}")
        return False


def import_cdl_xml(clips: List[Any], input_path: str, dry_run: bool = False) -> int:
    """
    Import CDL data from ASC CDL XML file.

    Args:
        clips: List of clips to apply CDL to
        input_path: Input CDL file path
        dry_run: If True, don't actually apply

    Returns:
        Number of clips updated
    """
    try:
        # Parse XML
        tree = ET.parse(input_path)
        root = tree.getroot()

        # Handle namespace
        ns = {'cdl': 'urn:ASC:CDL:v1.2'}

        # Extract ColorCorrections
        cdl_data = {}

        for cc in root.findall('.//cdl:ColorCorrection', ns):
            clip_id = cc.get('id')

            # Get SOP values
            sop_node = cc.find('cdl:SOPNode', ns)
            if sop_node is not None:
                slope_elem = sop_node.find('cdl:Slope', ns)
                offset_elem = sop_node.find('cdl:Offset', ns)
                power_elem = sop_node.find('cdl:Power', ns)

                slope = [float(x) for x in slope_elem.text.split()] if slope_elem is not None else [1.0, 1.0, 1.0]
                offset = [float(x) for x in offset_elem.text.split()] if offset_elem is not None else [0.0, 0.0, 0.0]
                power = [float(x) for x in power_elem.text.split()] if power_elem is not None else [1.0, 1.0, 1.0]

                # Add alpha channel (always 1.0 for RGB operations)
                slope.append(1.0)
                offset.append(0.0)
                power.append(1.0)
            else:
                slope = [1.0, 1.0, 1.0, 1.0]
                offset = [0.0, 0.0, 0.0, 0.0]
                power = [1.0, 1.0, 1.0, 1.0]

            # Get Saturation
            sat_node = cc.find('cdl:SatNode', ns)
            if sat_node is not None:
                sat_elem = sat_node.find('cdl:Saturation', ns)
                saturation = float(sat_elem.text) if sat_elem is not None else 1.0
            else:
                saturation = 1.0

            cdl_data[clip_id] = {
                'slope': slope,
                'offset': offset,
                'power': power,
                'saturation': saturation
            }

        # Also try without namespace (for compatibility)
        if not cdl_data:
            for cc in root.findall('.//ColorCorrection'):
                clip_id = cc.get('id')

                sop_node = cc.find('SOPNode')
                if sop_node is not None:
                    slope_elem = sop_node.find('Slope')
                    offset_elem = sop_node.find('Offset')
                    power_elem = sop_node.find('Power')

                    slope = [float(x) for x in slope_elem.text.split()] if slope_elem is not None else [1.0, 1.0, 1.0]
                    offset = [float(x) for x in offset_elem.text.split()] if offset_elem is not None else [0.0, 0.0, 0.0]
                    power = [float(x) for x in power_elem.text.split()] if power_elem is not None else [1.0, 1.0, 1.0]

                    slope.append(1.0)
                    offset.append(0.0)
                    power.append(1.0)
                else:
                    slope = [1.0, 1.0, 1.0, 1.0]
                    offset = [0.0, 0.0, 0.0, 0.0]
                    power = [1.0, 1.0, 1.0, 1.0]

                sat_node = cc.find('SatNode')
                if sat_node is not None:
                    sat_elem = sat_node.find('Saturation')
                    saturation = float(sat_elem.text) if sat_elem is not None else 1.0
                else:
                    saturation = 1.0

                cdl_data[clip_id] = {
                    'slope': slope,
                    'offset': offset,
                    'power': power,
                    'saturation': saturation
                }

        if not cdl_data:
            print("No CDL data found in file")
            return 0

        print(f"Loaded {len(cdl_data)} CDL correction(s) from file")
        print()

        # Apply to clips
        applied = 0

        for clip in clips:
            clip_name = clip.GetName()

            # Try to find matching CDL by clip name
            cdl = cdl_data.get(clip_name)

            if not cdl:
                # Try partial match
                for cdl_id, cdl_values in cdl_data.items():
                    if cdl_id in clip_name or clip_name in cdl_id:
                        cdl = cdl_values
                        break

            if cdl:
                if dry_run:
                    print(f"  Would apply CDL to: {clip_name}")
                    applied += 1
                else:
                    success = set_cdl_to_clip(clip, cdl)
                    if success:
                        print(f"  ✅ Applied CDL to: {clip_name}")
                        applied += 1
                    else:
                        print(f"  ❌ Failed to apply: {clip_name}")
            else:
                print(f"  ⚠️  No matching CDL for: {clip_name}")

        return applied

    except Exception as e:
        print(f"Error importing CDL: {e}")
        return 0


def show_cdl_info(clips: List[Any]) -> None:
    """
    Show CDL information for clips.

    Args:
        clips: List of clips
    """
    print("CDL Information:")
    print()

    for clip in clips:
        clip_name = clip.GetName()
        cdl = get_cdl_from_clip(clip)

        print(f"📹 {clip_name}")

        if cdl:
            print(f"   Slope:  [{cdl['slope'][0]:.3f}, {cdl['slope'][1]:.3f}, {cdl['slope'][2]:.3f}]")
            print(f"   Offset: [{cdl['offset'][0]:.3f}, {cdl['offset'][1]:.3f}, {cdl['offset'][2]:.3f}]")
            print(f"   Power:  [{cdl['power'][0]:.3f}, {cdl['power'][1]:.3f}, {cdl['power'][2]:.3f}]")
            print(f"   Saturation: {cdl['saturation']:.3f}")
        else:
            print("   No CDL data")

        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CDL Export/Import tool for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export CDL from all clips
  %(prog)s --export output.cdl --all

  # Export from specific track
  %(prog)s --export track1.cdl --track 1

  # Import CDL to all clips
  %(prog)s --import input.cdl --all

  # Show CDL info
  %(prog)s --info --all

  # Dry run import
  %(prog)s --import input.cdl --all --dry-run

CDL Format:
  ASC CDL (American Society of Cinematographers Color Decision List)
  - Industry standard for color grading interchange
  - Compatible with: Baselight, Nuke, Adobe apps, etc.
  - Contains: Slope, Offset, Power, Saturation
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export CDL to file (.cdl or .xml)'
    )

    mode_group.add_argument(
        '--import',
        type=str,
        metavar='FILE',
        dest='import_file',
        help='Import CDL from file (.cdl or .xml)'
    )

    mode_group.add_argument(
        '--info',
        action='store_true',
        help='Show CDL information for clips'
    )

    # Target selection
    target_group = parser.add_mutually_exclusive_group(required=True)

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

    # Other options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without applying (import only)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DaVinci Resolve CDL Export/Import Tool")
    print("=" * 70)
    print()

    if args.dry_run and not args.import_file:
        print("Warning: --dry-run only applies to --import operations")
        print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be applied")
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

    # Get target clips
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

    # Execute operation
    if args.export:
        print(f"Exporting CDL to: {args.export}")
        print()

        success = export_cdl_xml(target_clips, args.export, timeline_name)

        print()
        print("=" * 70)

        if success:
            print(f"✅ Successfully exported CDL to: {args.export}")
            print(f"   {len(target_clips)} clip(s) included")
        else:
            print("❌ Export failed")

    elif args.import_file:
        print(f"Importing CDL from: {args.import_file}")
        print()

        if not os.path.exists(args.import_file):
            print(f"❌ File not found: {args.import_file}")
            sys.exit(1)

        applied = import_cdl_xml(target_clips, args.import_file, dry_run=args.dry_run)

        print()
        print("=" * 70)

        if args.dry_run:
            print(f"Would apply CDL to {applied} clip(s)")
        else:
            print(f"✅ Applied CDL to {applied} clip(s)")

    elif args.info:
        show_cdl_info(target_clips)

        print("=" * 70)

    print("=" * 70)


if __name__ == "__main__":
    main()
