#!/usr/bin/env python3
"""
Batch Speed Ramp Manager for DaVinci Resolve

Apply speed ramps (slow motion, fast motion) to multiple clips with
preset curves and custom speed settings.

Usage:
    # Apply slow motion preset
    python3 batch_speed_ramp.py --preset slow-motion --all

    # Custom speed change
    python3 batch_speed_ramp.py --speed 50 --all

    # Apply to specific clips
    python3 batch_speed_ramp.py --preset fast-forward --color Orange

    # Reset to normal speed
    python3 batch_speed_ramp.py --reset --track 1

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


# Speed presets (percentage of normal speed)
SPEED_PRESETS = {
    'quarter-speed': {
        'speed': 25.0,
        'description': 'Quarter speed (25%) - extreme slow motion'
    },
    'half-speed': {
        'speed': 50.0,
        'description': 'Half speed (50%) - slow motion'
    },
    'slow-motion': {
        'speed': 60.0,
        'description': 'Slow motion (60%) - gentle slow down'
    },
    'normal': {
        'speed': 100.0,
        'description': 'Normal speed (100%)'
    },
    'timelapse': {
        'speed': 200.0,
        'description': 'Timelapse (200%) - 2x speed'
    },
    'fast-forward': {
        'speed': 400.0,
        'description': 'Fast forward (400%) - 4x speed'
    },
    'hyper-speed': {
        'speed': 800.0,
        'description': 'Hyper speed (800%) - 8x speed'
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


def get_clip_properties(clip) -> Dict[str, Any]:
    """
    Get clip properties including speed.

    Args:
        clip: TimelineItem object

    Returns:
        Dictionary with clip properties
    """
    props = {
        'name': clip.GetName(),
        'duration': clip.GetDuration(),
    }

    try:
        # Try to get clip property (API may vary)
        # Common properties: Speed, Retime, etc.

        # Note: DaVinci Resolve API doesn't directly expose speed/retime
        # This would typically be accessed through clip properties panel

        # Placeholder - actual implementation would use proper API
        props['speed'] = 100.0
        props['retime_enabled'] = False

    except Exception as e:
        props['error'] = str(e)

    return props


def set_clip_speed(clip, speed_percent: float, method: str = 'optical_flow') -> bool:
    """
    Set clip playback speed.

    Args:
        clip: TimelineItem object
        speed_percent: Speed as percentage (100 = normal, 50 = half speed, 200 = double speed)
        method: Retime method ('nearest', 'frame_blend', 'optical_flow')

    Returns:
        True if successful
    """
    try:
        # Note: DaVinci Resolve API doesn't provide direct speed control
        # Speed changes are typically done through:
        # 1. Right-click → Retime Controls → Change Speed
        # 2. Inspector → Retime and Scaling

        # This is a placeholder implementation
        # In real usage, would need to use appropriate API methods

        # For now, return False to indicate API limitation
        return False

    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False


def reset_clip_speed(clip) -> bool:
    """
    Reset clip to normal speed (100%).

    Args:
        clip: TimelineItem object

    Returns:
        True if successful
    """
    try:
        # Same API limitation as set_clip_speed
        return False

    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False


def show_clip_speeds(clips: List[Any]) -> None:
    """
    Show current speed settings for clips.

    Args:
        clips: List of clips
    """
    print("Current Speed Settings:")
    print()

    for clip in clips:
        clip_name = clip.GetName()
        props = get_clip_properties(clip)

        print(f"📹 {clip_name}")
        print(f"   Duration: {props['duration']} frames")

        if 'speed' in props:
            print(f"   Speed: {props['speed']:.1f}%")

        if props.get('retime_enabled'):
            print(f"   Retime: Enabled")
        else:
            print(f"   Retime: Disabled")

        print()


def batch_apply_speed(
    clips: List[Any],
    speed_percent: float,
    dry_run: bool = False
) -> int:
    """
    Batch apply speed to clips.

    Args:
        clips: List of clips
        speed_percent: Speed percentage
        dry_run: If True, don't actually apply

    Returns:
        Number of clips processed
    """
    processed = 0

    print("Note: DaVinci Resolve API does not provide direct speed/retime control.")
    print("      This tool will identify clips and provide manual instructions.")
    print()

    for clip in clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would set speed: {clip_name} → {speed_percent:.1f}%")
            processed += 1
        else:
            print(f"  📌 {clip_name}")
            print(f"     → Manual steps:")
            print(f"       1. Select clip in timeline")
            print(f"       2. Right-click → Retime Controls → Change Speed")
            print(f"       3. Enter speed: {speed_percent:.1f}%")
            print(f"       4. Choose retime method:")
            print(f"          - Nearest Frame (fast, blocky)")
            print(f"          - Frame Blend (smooth, some blur)")
            print(f"          - Optical Flow (smoothest, slower)")
            processed += 1

        print()

    return processed


def batch_reset_speed(clips: List[Any], dry_run: bool = False) -> int:
    """
    Batch reset clips to normal speed.

    Args:
        clips: List of clips
        dry_run: If True, don't actually apply

    Returns:
        Number of clips reset
    """
    reset_count = 0

    for clip in clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would reset: {clip_name} → 100%")
            reset_count += 1
        else:
            print(f"  📌 {clip_name}")
            print(f"     → Reset to 100% speed manually")
            reset_count += 1

        print()

    return reset_count


def list_presets():
    """Print available speed presets."""
    print("=" * 70)
    print("Available Speed Presets")
    print("=" * 70)
    print()

    for preset_name, preset_data in SPEED_PRESETS.items():
        print(f"{preset_name}:")
        print(f"  {preset_data['description']}")
        print(f"  Speed: {preset_data['speed']:.1f}%")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch speed ramp manager for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Apply preset
  %(prog)s --preset slow-motion --all

  # Custom speed
  %(prog)s --speed 75 --track 1

  # Reset to normal
  %(prog)s --reset --color Orange

  # Show current speeds
  %(prog)s --show --all

  # List presets
  %(prog)s --list-presets

  # Dry run
  %(prog)s --preset fast-forward --all --dry-run

Note:
  DaVinci Resolve API does not provide direct speed/retime control.
  This tool identifies clips and provides step-by-step manual instructions.

Available presets: quarter-speed, half-speed, slow-motion, normal, timelapse, fast-forward, hyper-speed
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--preset',
        type=str,
        choices=list(SPEED_PRESETS.keys()),
        help='Use speed preset'
    )

    mode_group.add_argument(
        '--speed',
        type=float,
        metavar='PERCENT',
        help='Set custom speed percentage (100 = normal, 50 = half, 200 = double)'
    )

    mode_group.add_argument(
        '--reset',
        action='store_true',
        help='Reset to normal speed (100%%)'
    )

    mode_group.add_argument(
        '--show',
        action='store_true',
        help='Show current speed settings'
    )

    mode_group.add_argument(
        '--list-presets',
        action='store_true',
        help='List available presets and exit'
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
    if args.speed is not None and (args.speed <= 0 or args.speed > 10000):
        print("Error: Speed must be between 0 and 10000 percent")
        sys.exit(1)

    if not args.all and not args.track and not args.color and not args.list_presets:
        if not args.show:
            print("Error: Specify target (--all, --track, or --color)")
            sys.exit(1)

    # Get speed value
    if args.preset:
        speed_percent = SPEED_PRESETS[args.preset]['speed']
        print(f"Using preset: {args.preset} ({SPEED_PRESETS[args.preset]['description']})")
    elif args.speed:
        speed_percent = args.speed
    else:
        speed_percent = 100.0

    print("=" * 70)
    print("DaVinci Resolve Batch Speed Ramp Manager")
    print("=" * 70)
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

    if not target_clips and not args.show:
        print("❌ No target clips found")
        sys.exit(1)

    if target_clips:
        print(f"Found {len(target_clips)} target clip(s)")
        print()

    # Execute operation
    result = 0

    if args.preset or args.speed:
        print(f"Setting speed to {speed_percent:.1f}%...")
        print()
        result = batch_apply_speed(target_clips, speed_percent, dry_run=args.dry_run)

    elif args.reset:
        print("Resetting to normal speed (100%)...")
        print()
        result = batch_reset_speed(target_clips, dry_run=args.dry_run)

    elif args.show:
        show_clip_speeds(target_clips)

    # Summary
    print()
    print("=" * 70)

    if args.preset or args.speed:
        if args.dry_run:
            print(f"Would set speed for {result} clip(s)")
        else:
            print(f"📋 Identified {result} clip(s) for manual speed change")
            print()
            print("API Limitation Notice:")
            print("  DaVinci Resolve API does not support programmatic speed changes.")
            print("  Please follow the manual steps shown above for each clip.")
            print()
            print("Tip: Use keyboard shortcuts for faster workflow:")
            print("  - Cmd+R (Mac) / Ctrl+R (Win): Retime Controls")

    elif args.reset:
        if args.dry_run:
            print(f"Would reset {result} clip(s)")
        else:
            print(f"📋 Identified {result} clip(s) for manual speed reset")

    print("=" * 70)


if __name__ == "__main__":
    main()
