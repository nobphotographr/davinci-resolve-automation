#!/usr/bin/env python3
"""
Proxy Workflow Manager for DaVinci Resolve

Manage proxy media workflow: enable/disable proxies, check proxy status,
and generate proxy creation reports for offline/online workflows.

Usage:
    # Check proxy status
    python3 proxy_workflow_manager.py --status --all

    # Enable proxy mode
    python3 proxy_workflow_manager.py --enable --all

    # Disable proxy mode (use original media)
    python3 proxy_workflow_manager.py --disable --all

    # Generate proxy report
    python3 proxy_workflow_manager.py --report proxies.csv

    # Check clips without proxies
    python3 proxy_workflow_manager.py --check-missing --all

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
import csv
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


def get_proxy_info(clip) -> Dict[str, Any]:
    """
    Get proxy information for a clip.

    Args:
        clip: TimelineItem object

    Returns:
        Dictionary with proxy info
    """
    info = {
        'name': clip.GetName(),
        'has_proxy': False,
        'proxy_enabled': False,
        'proxy_path': None,
        'original_path': None,
    }

    try:
        # Note: DaVinci Resolve API has limited proxy access
        # Typical proxy workflow:
        # 1. Generate proxies via Media Pool
        # 2. Toggle proxy mode via Playback menu
        # 3. Check proxy status in Media Pool

        # Get media pool item
        media_pool_item = clip.GetMediaPoolItem()

        if media_pool_item:
            # Try to get clip properties
            clip_props = media_pool_item.GetClipProperty()

            if clip_props:
                # Check for proxy-related properties
                # Note: Actual property names may vary
                info['original_path'] = clip_props.get('File Path', 'Unknown')

                # Proxy detection heuristics
                # DaVinci Resolve typically stores proxies in project's Cache/Proxy Media folder
                if 'proxy' in info['original_path'].lower():
                    info['has_proxy'] = True
                    info['proxy_path'] = info['original_path']

    except Exception as e:
        info['error'] = str(e)

    return info


def check_proxy_status(clips: List[Any]) -> Dict[str, List[Any]]:
    """
    Check proxy status for all clips.

    Args:
        clips: List of clips

    Returns:
        Dictionary categorizing clips by proxy status
    """
    status = {
        'with_proxy': [],
        'without_proxy': [],
        'unknown': []
    }

    for clip in clips:
        info = get_proxy_info(clip)

        if info.get('has_proxy'):
            status['with_proxy'].append(clip)
        elif info.get('error'):
            status['unknown'].append(clip)
        else:
            status['without_proxy'].append(clip)

    return status


def show_proxy_status(clips: List[Any]) -> None:
    """
    Display proxy status for clips.

    Args:
        clips: List of clips
    """
    print("Proxy Status Report:")
    print()

    for clip in clips:
        info = get_proxy_info(clip)
        clip_name = info['name']

        print(f"📹 {clip_name}")

        if info.get('has_proxy'):
            print(f"   ✅ Has proxy")
            if info.get('proxy_path'):
                print(f"   Path: {info['proxy_path']}")
        else:
            print(f"   ⚠️  No proxy found")

        if info.get('original_path'):
            print(f"   Original: {info['original_path']}")

        if info.get('error'):
            print(f"   ❌ Error: {info['error']}")

        print()


def enable_proxy_mode(project) -> bool:
    """
    Enable proxy mode for project.

    Args:
        project: Project object

    Returns:
        True if successful
    """
    try:
        # Note: DaVinci Resolve API doesn't provide direct proxy mode toggle
        # Proxy mode is controlled via:
        # Playback → Proxy Mode → [Half Resolution / Quarter Resolution / etc.]

        # This is a placeholder
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def disable_proxy_mode(project) -> bool:
    """
    Disable proxy mode (use original media).

    Args:
        project: Project object

    Returns:
        True if successful
    """
    try:
        # Same API limitation
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def generate_proxy_report(clips: List[Any], output_path: str) -> bool:
    """
    Generate CSV report of proxy status.

    Args:
        clips: List of clips
        output_path: Output CSV file path

    Returns:
        True if successful
    """
    try:
        fieldnames = [
            'clip_name',
            'has_proxy',
            'original_path',
            'proxy_path',
            'status'
        ]

        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for clip in clips:
                info = get_proxy_info(clip)

                row = {
                    'clip_name': info['name'],
                    'has_proxy': 'Yes' if info.get('has_proxy') else 'No',
                    'original_path': info.get('original_path', ''),
                    'proxy_path': info.get('proxy_path', ''),
                    'status': 'Error' if info.get('error') else 'OK'
                }

                writer.writerow(row)

        return True

    except Exception as e:
        print(f"Error generating report: {e}")
        return False


def suggest_proxy_workflow() -> None:
    """Print proxy workflow suggestions."""
    print("=" * 70)
    print("Recommended Proxy Workflow")
    print("=" * 70)
    print()
    print("1. Generate Proxies:")
    print("   • Media Pool → Select clips")
    print("   • Right-click → Generate Proxy Media")
    print("   • Choose format: ProRes Proxy / DNxHR LB / H.264")
    print("   • Set resolution: 1/2 or 1/4 of original")
    print()
    print("2. Enable Proxy Mode:")
    print("   • Playback → Proxy Mode → Half Resolution")
    print("   • Or: Playback → Proxy Mode → Quarter Resolution")
    print()
    print("3. Edit with Proxies:")
    print("   • Work with lightweight proxy files")
    print("   • Faster playback and scrubbing")
    print()
    print("4. Disable Proxy Mode for Delivery:")
    print("   • Playback → Proxy Mode → Off")
    print("   • Render with original high-quality media")
    print()
    print("Proxy Media Location:")
    print("   Project → [Project Name] → CacheClip → Proxy Media")
    print()
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Proxy workflow manager for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check proxy status
  %(prog)s --status --all

  # Enable proxy mode
  %(prog)s --enable

  # Disable proxy mode
  %(prog)s --disable

  # Generate proxy report
  %(prog)s --report proxies.csv

  # Check clips without proxies
  %(prog)s --check-missing --all

  # Show workflow guide
  %(prog)s --workflow-guide

Note:
  DaVinci Resolve API has limited proxy control.
  This tool provides status checking and workflow guidance.
  Use Playback → Proxy Mode menu to toggle proxy mode manually.
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--status',
        action='store_true',
        help='Show proxy status for clips'
    )

    mode_group.add_argument(
        '--enable',
        action='store_true',
        help='Enable proxy mode (manual steps provided)'
    )

    mode_group.add_argument(
        '--disable',
        action='store_true',
        help='Disable proxy mode (manual steps provided)'
    )

    mode_group.add_argument(
        '--report',
        type=str,
        metavar='FILE',
        help='Generate proxy status report (CSV)'
    )

    mode_group.add_argument(
        '--check-missing',
        action='store_true',
        help='Check for clips without proxies'
    )

    mode_group.add_argument(
        '--workflow-guide',
        action='store_true',
        help='Show recommended proxy workflow'
    )

    # Target selection (optional for some modes)
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

    args = parser.parse_args()

    # Show workflow guide
    if args.workflow_guide:
        suggest_proxy_workflow()
        return

    print("=" * 70)
    print("DaVinci Resolve Proxy Workflow Manager")
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

        if not timeline and (args.status or args.check_missing or args.report):
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

    # Execute operation
    if args.enable:
        print("Enabling Proxy Mode:")
        print()
        print("Note: DaVinci Resolve API does not support proxy mode control.")
        print()
        print("Manual steps:")
        print("  1. Go to Playback menu")
        print("  2. Select Proxy Mode → Half Resolution")
        print("     (or Quarter Resolution for even lighter proxies)")
        print()
        print("This will use proxy media for all clips that have proxies.")
        print()

    elif args.disable:
        print("Disabling Proxy Mode (Use Original Media):")
        print()
        print("Note: DaVinci Resolve API does not support proxy mode control.")
        print()
        print("Manual steps:")
        print("  1. Go to Playback menu")
        print("  2. Select Proxy Mode → Off")
        print()
        print("This will use original high-quality media for rendering.")
        print()

    elif args.status or args.check_missing or args.report:
        # Get target clips
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

        if args.status:
            show_proxy_status(target_clips)

        elif args.check_missing:
            print("Checking for clips without proxies...")
            print()

            status = check_proxy_status(target_clips)

            if status['without_proxy']:
                print(f"⚠️  Clips without proxies ({len(status['without_proxy'])}):")
                for clip in status['without_proxy']:
                    print(f"   • {clip.GetName()}")
                print()

                print("To generate proxies:")
                print("  1. Select these clips in Media Pool")
                print("  2. Right-click → Generate Proxy Media")
                print("  3. Choose format and resolution")
            else:
                print("✅ All clips have proxies")

            print()

            if status['with_proxy']:
                print(f"✅ Clips with proxies ({len(status['with_proxy'])}):")
                for clip in status['with_proxy']:
                    print(f"   • {clip.GetName()}")

        elif args.report:
            print(f"Generating proxy report: {args.report}")
            print()

            success = generate_proxy_report(target_clips, args.report)

            print()
            print("=" * 70)

            if success:
                print(f"✅ Successfully generated proxy report: {args.report}")
                print(f"   {len(target_clips)} clip(s) included")
            else:
                print("❌ Report generation failed")

    print("=" * 70)


if __name__ == "__main__":
    main()
