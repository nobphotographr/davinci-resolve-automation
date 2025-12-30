#!/usr/bin/env python3
"""
Batch Stabilization Manager for DaVinci Resolve

Batch enable/disable and configure stabilization settings across multiple clips.
Useful for managing camera shake correction on large projects.

Usage:
    # Enable stabilization with preset
    python3 batch_stabilization_manager.py --enable --preset smooth --all

    # Disable stabilization
    python3 batch_stabilization_manager.py --disable --track 1

    # Check stabilization status
    python3 batch_stabilization_manager.py --status --all

    # Enable with custom settings
    python3 batch_stabilization_manager.py --enable --strength 0.8 --smoothness 0.5 --all

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


# Stabilization presets
STABILIZATION_PRESETS = {
    'light': {
        'strength': 0.3,
        'smoothness': 0.2,
        'description': 'Light stabilization for subtle shake'
    },
    'normal': {
        'strength': 0.5,
        'smoothness': 0.4,
        'description': 'Normal stabilization for general use'
    },
    'smooth': {
        'strength': 0.7,
        'smoothness': 0.6,
        'description': 'Smooth stabilization for handheld footage'
    },
    'strong': {
        'strength': 0.9,
        'smoothness': 0.8,
        'description': 'Strong stabilization for heavy shake'
    },
    'perspective': {
        'strength': 0.6,
        'smoothness': 0.5,
        'description': 'Perspective-aware stabilization'
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


def check_stabilization_status(clip) -> Dict[str, Any]:
    """
    Check stabilization status for a clip.

    Args:
        clip: TimelineItem object

    Returns:
        Dictionary with stabilization info
    """
    status = {
        'enabled': False,
        'mode': 'Unknown',
        'strength': 0.0,
    }

    try:
        # Note: DaVinci Resolve API may not expose stabilization settings directly
        # This is a placeholder implementation
        # Actual implementation would need to check clip properties

        # Get clip properties
        # In real implementation, would check:
        # - clip.GetProperty('Stabilization')
        # - or similar API calls

        # For now, return placeholder status
        status['enabled'] = False
        status['mode'] = 'Not Available via API'

    except Exception as e:
        status['mode'] = f'Error: {e}'

    return status


def enable_stabilization(
    clip,
    strength: float = 0.5,
    smoothness: float = 0.4,
    mode: str = 'Perspective'
) -> bool:
    """
    Enable stabilization for a clip.

    Args:
        clip: TimelineItem object
        strength: Stabilization strength (0.0 to 1.0)
        smoothness: Smoothness amount (0.0 to 1.0)
        mode: Stabilization mode

    Returns:
        True if successful
    """
    try:
        # Note: DaVinci Resolve API does not directly support stabilization settings
        # Stabilization is typically accessed through:
        # - Inspector panel in UI
        # - Tracker window

        # This is a placeholder implementation
        # In a real scenario, users would need to:
        # 1. Select clips
        # 2. Open Inspector
        # 3. Enable stabilization manually

        # Return False to indicate API limitation
        return False

    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False


def disable_stabilization(clip) -> bool:
    """
    Disable stabilization for a clip.

    Args:
        clip: TimelineItem object

    Returns:
        True if successful
    """
    try:
        # Note: Same API limitation as enable_stabilization
        return False

    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False


def analyze_stabilization_needs(clips: List[Any]) -> Dict[str, List[Any]]:
    """
    Analyze clips and suggest stabilization candidates.

    Args:
        clips: List of clips

    Returns:
        Dictionary categorizing clips by suggested stabilization level
    """
    suggestions = {
        'needs_stabilization': [],
        'already_stable': [],
        'unknown': []
    }

    for clip in clips:
        clip_name = clip.GetName()

        # Heuristic: Check clip name for indicators
        name_lower = clip_name.lower()

        if any(keyword in name_lower for keyword in ['handheld', 'shake', 'unstable', 'gimbal']):
            suggestions['needs_stabilization'].append(clip)
        elif any(keyword in name_lower for keyword in ['tripod', 'locked', 'static', 'fixed']):
            suggestions['already_stable'].append(clip)
        else:
            suggestions['unknown'].append(clip)

    return suggestions


def show_stabilization_status(clips: List[Any]) -> None:
    """
    Show stabilization status for all clips.

    Args:
        clips: List of clips
    """
    print("Stabilization Status:")
    print()

    for clip in clips:
        clip_name = clip.GetName()
        status = check_stabilization_status(clip)

        print(f"📹 {clip_name}")
        print(f"   Enabled: {status['enabled']}")
        print(f"   Mode: {status['mode']}")
        if status['strength'] > 0:
            print(f"   Strength: {status['strength']:.2f}")
        print()


def batch_enable_stabilization(
    clips: List[Any],
    strength: float,
    smoothness: float,
    dry_run: bool = False
) -> int:
    """
    Batch enable stabilization.

    Args:
        clips: List of clips
        strength: Stabilization strength
        smoothness: Smoothness amount
        dry_run: If True, don't actually apply

    Returns:
        Number of clips enabled
    """
    enabled = 0

    print("Note: DaVinci Resolve API does not provide direct stabilization control.")
    print("      This tool will identify clips and provide manual instructions.")
    print()

    for clip in clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would enable: {clip_name}")
            print(f"    Strength: {strength:.2f}, Smoothness: {smoothness:.2f}")
            enabled += 1
        else:
            print(f"  📌 {clip_name}")
            print(f"     → Manual steps:")
            print(f"       1. Select clip in timeline")
            print(f"       2. Open Inspector panel")
            print(f"       3. Navigate to Stabilization section")
            print(f"       4. Enable stabilization")
            print(f"       5. Set Strength: {strength:.2f}")
            print(f"       6. Set Smoothness: {smoothness:.2f}")
            enabled += 1

        print()

    return enabled


def batch_disable_stabilization(clips: List[Any], dry_run: bool = False) -> int:
    """
    Batch disable stabilization.

    Args:
        clips: List of clips
        dry_run: If True, don't actually apply

    Returns:
        Number of clips disabled
    """
    disabled = 0

    for clip in clips:
        clip_name = clip.GetName()

        if dry_run:
            print(f"  Would disable: {clip_name}")
            disabled += 1
        else:
            print(f"  📌 {clip_name}")
            print(f"     → Disable stabilization in Inspector panel")
            disabled += 1

        print()

    return disabled


def list_presets():
    """Print available stabilization presets."""
    print("=" * 70)
    print("Available Stabilization Presets")
    print("=" * 70)
    print()

    for preset_name, preset_data in STABILIZATION_PRESETS.items():
        print(f"{preset_name}:")
        print(f"  {preset_data['description']}")
        print(f"  Strength: {preset_data['strength']:.2f}")
        print(f"  Smoothness: {preset_data['smoothness']:.2f}")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch stabilization manager for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enable with preset
  %(prog)s --enable --preset smooth --all

  # Enable with custom settings
  %(prog)s --enable --strength 0.7 --smoothness 0.6 --track 1

  # Disable stabilization
  %(prog)s --disable --color Orange

  # Check status
  %(prog)s --status --all

  # Analyze clips for stabilization needs
  %(prog)s --analyze --all

  # List presets
  %(prog)s --list-presets

  # Dry run
  %(prog)s --enable --preset normal --all --dry-run

Note:
  DaVinci Resolve API does not provide direct stabilization control.
  This tool identifies clips and provides step-by-step manual instructions.

Available presets: light, normal, smooth, strong, perspective
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--enable',
        action='store_true',
        help='Enable stabilization'
    )

    mode_group.add_argument(
        '--disable',
        action='store_true',
        help='Disable stabilization'
    )

    mode_group.add_argument(
        '--status',
        action='store_true',
        help='Show stabilization status'
    )

    mode_group.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze clips and suggest stabilization needs'
    )

    mode_group.add_argument(
        '--list-presets',
        action='store_true',
        help='List available presets and exit'
    )

    # Preset or custom settings
    settings_group = parser.add_argument_group('Stabilization settings')

    settings_group.add_argument(
        '--preset',
        type=str,
        choices=list(STABILIZATION_PRESETS.keys()),
        help='Use stabilization preset'
    )

    settings_group.add_argument(
        '--strength',
        type=float,
        metavar='VALUE',
        help='Stabilization strength (0.0 to 1.0)'
    )

    settings_group.add_argument(
        '--smoothness',
        type=float,
        metavar='VALUE',
        help='Smoothness amount (0.0 to 1.0)'
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
    if args.enable:
        if not args.preset and (args.strength is None or args.smoothness is None):
            print("Error: When using --enable, specify --preset or both --strength and --smoothness")
            sys.exit(1)

        if args.strength is not None and (args.strength < 0.0 or args.strength > 1.0):
            print("Error: Strength must be between 0.0 and 1.0")
            sys.exit(1)

        if args.smoothness is not None and (args.smoothness < 0.0 or args.smoothness > 1.0):
            print("Error: Smoothness must be between 0.0 and 1.0")
            sys.exit(1)

    if not args.all and not args.track and not args.color and not args.list_presets:
        if not args.analyze and not args.status:
            print("Error: Specify target (--all, --track, or --color)")
            sys.exit(1)

    # Get settings
    if args.enable:
        if args.preset:
            preset = STABILIZATION_PRESETS[args.preset]
            strength = preset['strength']
            smoothness = preset['smoothness']
            print(f"Using preset: {args.preset} ({preset['description']})")
        else:
            strength = args.strength
            smoothness = args.smoothness
    else:
        strength = 0.0
        smoothness = 0.0

    print("=" * 70)
    print("DaVinci Resolve Batch Stabilization Manager")
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

    if not target_clips and not args.status and not args.analyze:
        print("❌ No target clips found")
        sys.exit(1)

    if target_clips:
        print(f"Found {len(target_clips)} target clip(s)")
        print()

    # Execute operation
    result = 0

    if args.enable:
        print(f"Enabling stabilization (Strength: {strength:.2f}, Smoothness: {smoothness:.2f})...")
        print()
        result = batch_enable_stabilization(target_clips, strength, smoothness, dry_run=args.dry_run)

    elif args.disable:
        print("Disabling stabilization...")
        print()
        result = batch_disable_stabilization(target_clips, dry_run=args.dry_run)

    elif args.status:
        show_stabilization_status(target_clips)

    elif args.analyze:
        print("Analyzing clips for stabilization needs...")
        print()

        suggestions = analyze_stabilization_needs(target_clips)

        if suggestions['needs_stabilization']:
            print(f"🔴 Likely needs stabilization ({len(suggestions['needs_stabilization'])} clips):")
            for clip in suggestions['needs_stabilization']:
                print(f"   • {clip.GetName()}")
            print()

        if suggestions['already_stable']:
            print(f"🟢 Likely already stable ({len(suggestions['already_stable'])} clips):")
            for clip in suggestions['already_stable']:
                print(f"   • {clip.GetName()}")
            print()

        if suggestions['unknown']:
            print(f"⚪ Unknown ({len(suggestions['unknown'])} clips):")
            for clip in suggestions['unknown']:
                print(f"   • {clip.GetName()}")
            print()

        result = len(suggestions['needs_stabilization'])

    # Summary
    print()
    print("=" * 70)

    if args.enable:
        if args.dry_run:
            print(f"Would enable stabilization for {result} clip(s)")
        else:
            print(f"📋 Identified {result} clip(s) for manual stabilization")
            print()
            print("API Limitation Notice:")
            print("  DaVinci Resolve API does not support programmatic stabilization.")
            print("  Please follow the manual steps shown above for each clip.")
            print()
            print("Alternative: Use Tracker window's Camera Lock feature")
            print("  1. Window → Tracker")
            print("  2. Select clip")
            print("  3. Camera Lock → Stabilize")

    elif args.disable:
        if args.dry_run:
            print(f"Would disable stabilization for {result} clip(s)")
        else:
            print(f"📋 Identified {result} clip(s) for manual stabilization disable")

    elif args.analyze:
        if args.dry_run:
            print(f"Would analyze {len(target_clips)} clip(s)")
        else:
            print(f"✅ Analyzed {len(target_clips)} clip(s)")
            if result > 0:
                print(f"   {result} clip(s) likely need stabilization")

    print("=" * 70)


if __name__ == "__main__":
    main()
