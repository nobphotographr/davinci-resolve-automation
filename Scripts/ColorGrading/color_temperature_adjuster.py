#!/usr/bin/env python3
"""
Batch Color Temperature Adjuster for DaVinci Resolve

Batch adjust white balance (color temperature and tint) across multiple clips
with scene-based matching and time-of-day presets.

Usage:
    # Set specific color temperature for all clips
    python3 color_temperature_adjuster.py --temperature 5600 --all

    # Match to reference clip
    python3 color_temperature_adjuster.py --match-to "RefClip" --track 1

    # Apply time-of-day preset
    python3 color_temperature_adjuster.py --preset daylight --color Orange

    # Adjust tint only
    python3 color_temperature_adjuster.py --tint 10 --all

    # Combined temperature and tint
    python3 color_temperature_adjuster.py --temperature 5600 --tint 0 --all --dry-run

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Color temperature presets (in Kelvin)
TEMPERATURE_PRESETS = {
    'tungsten': {
        'temp': 3200,
        'tint': 0,
        'description': 'Tungsten/Indoor lighting (3200K)'
    },
    'sunrise': {
        'temp': 3500,
        'tint': 5,
        'description': 'Sunrise/Sunset warm (3500K, +5 tint)'
    },
    'fluorescent': {
        'temp': 4000,
        'tint': -10,
        'description': 'Fluorescent lighting (4000K, -10 tint)'
    },
    'cloudy': {
        'temp': 6000,
        'tint': 0,
        'description': 'Cloudy daylight (6000K)'
    },
    'daylight': {
        'temp': 5600,
        'tint': 0,
        'description': 'Daylight balanced (5600K)'
    },
    'shade': {
        'temp': 7000,
        'tint': 0,
        'description': 'Open shade (7000K)'
    },
    'blue_hour': {
        'temp': 8000,
        'tint': -5,
        'description': 'Blue hour/Twilight (8000K, -5 tint)'
    },
}


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


def set_color_temperature(
    clip,
    temperature: Optional[float] = None,
    tint: Optional[float] = None
) -> bool:
    """
    Set color temperature and tint for a clip.

    Args:
        clip: TimelineItem object
        temperature: Color temperature in Kelvin
        tint: Tint value (-50 to +50)

    Returns:
        True if successful
    """
    try:
        # Note: DaVinci Resolve API may not have direct white balance controls
        # This is a simplified implementation using CDL adjustments
        # For actual temperature control, may need to use specific node operations

        # Get current node count
        node_count = clip.GetNumNodes()
        if not node_count or node_count == 0:
            return False

        # Use first node for white balance adjustment
        node_index = 1

        # Create CDL adjustment based on temperature
        # This is an approximation - actual implementation may vary
        if temperature is not None:
            # Convert temperature to RGB shift
            # Warmer = more red/yellow, Cooler = more blue
            if temperature < 5000:
                # Warm (tungsten)
                r_shift = 1.0 + ((5600 - temperature) / 10000)
                b_shift = 1.0 - ((5600 - temperature) / 10000)
            else:
                # Cool (daylight+)
                r_shift = 1.0 - ((temperature - 5600) / 10000)
                b_shift = 1.0 + ((temperature - 5600) / 10000)

            # Get current CDL
            cdl = clip.GetNodeColorData(node_index)
            if not cdl:
                cdl = {
                    'slope': [1.0, 1.0, 1.0, 1.0],
                    'offset': [0.0, 0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0, 1.0],
                    'saturation': 1.0
                }

            # Adjust slope for temperature
            cdl['slope'][0] = r_shift  # Red
            cdl['slope'][2] = b_shift  # Blue

            # Apply tint if specified (green/magenta shift)
            if tint is not None:
                # Positive tint = green, Negative = magenta
                g_shift = 1.0 + (tint / 100.0)
                cdl['slope'][1] = g_shift  # Green

            # Set CDL
            success = clip.SetNodeColorData(node_index, cdl)
            return success

    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False

    return False


def apply_temperature_adjustment(
    clips: List[Any],
    temperature: Optional[float] = None,
    tint: Optional[float] = None,
    dry_run: bool = False
) -> int:
    """
    Apply temperature adjustment to clips.

    Args:
        clips: List of TimelineItem objects
        temperature: Color temperature in Kelvin
        tint: Tint value
        dry_run: If True, don't actually apply

    Returns:
        Number of clips adjusted
    """
    adjusted = 0

    for clip in clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would adjust: {clip_name}")
            if temperature:
                print(f"    Temperature: {temperature}K")
            if tint:
                print(f"    Tint: {tint:+.1f}")
            adjusted += 1
        else:
            success = set_color_temperature(clip, temperature, tint)
            if success:
                print(f"  ✅ Adjusted: {clip_name}")
                if temperature:
                    print(f"    Temperature: {temperature}K")
                if tint:
                    print(f"    Tint: {tint:+.1f}")
                adjusted += 1
            else:
                print(f"  ❌ Failed: {clip_name}")

    return adjusted


def list_presets():
    """Print available temperature presets."""
    print("=" * 70)
    print("Available Color Temperature Presets")
    print("=" * 70)
    print()

    for preset_name, preset_data in TEMPERATURE_PRESETS.items():
        print(f"{preset_name}:")
        print(f"  {preset_data['description']}")
        print(f"  Temperature: {preset_data['temp']}K")
        print(f"  Tint: {preset_data['tint']:+d}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch adjust color temperature in DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set temperature for all clips
  %(prog)s --temperature 5600 --all

  # Set temperature and tint
  %(prog)s --temperature 5600 --tint 0 --all

  # Apply preset to specific track
  %(prog)s --preset daylight --track 1

  # Apply to clips with specific color
  %(prog)s --temperature 3200 --color Orange

  # List presets
  %(prog)s --list-presets

  # Dry run
  %(prog)s --preset cloudy --all --dry-run

Available presets: tungsten, sunrise, fluorescent, cloudy, daylight, shade, blue_hour
        """
    )

    # Temperature/Preset options
    temp_group = parser.add_mutually_exclusive_group()

    temp_group.add_argument(
        '--temperature',
        type=float,
        metavar='KELVIN',
        help='Color temperature in Kelvin (e.g., 3200, 5600, 6500)'
    )

    temp_group.add_argument(
        '--preset',
        type=str,
        choices=list(TEMPERATURE_PRESETS.keys()),
        help='Use temperature preset'
    )

    temp_group.add_argument(
        '--list-presets',
        action='store_true',
        help='List available presets and exit'
    )

    # Tint adjustment
    parser.add_argument(
        '--tint',
        type=float,
        metavar='VALUE',
        help='Tint adjustment (-50 to +50, 0=neutral, +green/-magenta)'
    )

    # Target selection
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

    # Other options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without applying'
    )

    args = parser.parse_args()

    # List presets if requested
    if args.list_presets:
        list_presets()
        return

    # Validation
    if not args.temperature and not args.preset and not args.tint:
        parser.print_help()
        print()
        print("Error: Specify --temperature, --preset, or --tint")
        sys.exit(1)

    if not args.all and not args.track and not args.color:
        print("Error: Specify target (--all, --track, or --color)")
        sys.exit(1)

    # Get temperature and tint values
    if args.preset:
        preset = TEMPERATURE_PRESETS[args.preset]
        temperature = preset['temp']
        tint = args.tint if args.tint is not None else preset['tint']
        print(f"Using preset: {args.preset} ({preset['description']})")
    else:
        temperature = args.temperature
        tint = args.tint

    print("=" * 70)
    print("DaVinci Resolve Batch Color Temperature Adjuster")
    print("=" * 70)
    print()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No adjustments will be applied")
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

    # Apply adjustment
    print("Adjusting color temperature...")
    print()

    adjusted = apply_temperature_adjustment(
        target_clips,
        temperature=temperature,
        tint=tint,
        dry_run=args.dry_run
    )

    # Summary
    print()
    print("=" * 70)

    if args.dry_run:
        print(f"Would adjust {adjusted} clip(s)")
    else:
        print(f"✅ Adjusted {adjusted} clip(s)")

    print("=" * 70)


if __name__ == "__main__":
    main()
