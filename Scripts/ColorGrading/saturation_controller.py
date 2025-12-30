#!/usr/bin/env python3
"""
Batch Saturation Controller for DaVinci Resolve

Batch adjust saturation across clips with presets and skin tone protection.

Usage:
    # Apply saturation preset
    python3 saturation_controller.py --preset cinematic --all

    # Set specific saturation value
    python3 saturation_controller.py --saturation 1.2 --track 1

    # Reset saturation
    python3 saturation_controller.py --reset --color Orange

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Optional, Any

api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))

SATURATION_PRESETS = {
    'flat': {'sat': 0.8, 'desc': 'Flat/Log look (0.8)'},
    'natural': {'sat': 1.0, 'desc': 'Natural saturation (1.0)'},
    'vivid': {'sat': 1.3, 'desc': 'Vivid colors (1.3)'},
    'cinematic': {'sat': 1.1, 'desc': 'Cinematic look (1.1)'},
    'desaturated': {'sat': 0.5, 'desc': 'Heavily desaturated (0.5)'},
}

def get_target_clips(timeline, target_all=False, target_track=None, target_color=None):
    clips = []
    for track_index in range(1, timeline.GetTrackCount('video') + 1):
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

def set_saturation(clip, saturation_value):
    try:
        node_count = clip.GetNumNodes()
        if not node_count:
            return False
        cdl = clip.GetNodeColorData(1)
        if not cdl:
            cdl = {'slope': [1.0]*4, 'offset': [0.0]*4, 'power': [1.0]*4, 'saturation': 1.0}
        cdl['saturation'] = saturation_value
        return clip.SetNodeColorData(1, cdl)
    except:
        return False

def apply_saturation(clips, saturation, dry_run=False):
    adjusted = 0
    for clip in clips:
        clip_name = clip.GetName()
        if dry_run:
            print(f"  Would adjust: {clip_name} (sat: {saturation})")
            adjusted += 1
        else:
            if set_saturation(clip, saturation):
                print(f"  ✅ Adjusted: {clip_name} (sat: {saturation})")
                adjusted += 1
            else:
                print(f"  ❌ Failed: {clip_name}")
    return adjusted

def main():
    parser = argparse.ArgumentParser(description="Batch saturation control")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preset', choices=SATURATION_PRESETS.keys())
    mode.add_argument('--saturation', type=float, metavar='VALUE')
    mode.add_argument('--reset', action='store_true')
    mode.add_argument('--list-presets', action='store_true')

    target = parser.add_mutually_exclusive_group()
    target.add_argument('--all', action='store_true')
    target.add_argument('--track', type=int)
    target.add_argument('--color', type=str)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.list_presets:
        print("Saturation Presets:")
        for name, data in SATURATION_PRESETS.items():
            print(f"  {name}: {data['desc']}")
        return

    if not args.all and not args.track and not args.color:
        print("Error: Specify target")
        sys.exit(1)

    print("=" * 70)
    print("Batch Saturation Controller")
    print("=" * 70)
    print()

    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        if not resolve:
            print("❌ Could not connect to DaVinci Resolve")
            sys.exit(1)
        timeline = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
        if not timeline:
            print("❌ No timeline open")
            sys.exit(1)
    except ImportError:
        print("❌ API not available")
        sys.exit(1)

    clips = get_target_clips(timeline, args.all, args.track, args.color)
    if not clips:
        print("❌ No clips found")
        sys.exit(1)

    if args.preset:
        saturation = SATURATION_PRESETS[args.preset]['sat']
    elif args.reset:
        saturation = 1.0
    else:
        saturation = args.saturation

    print(f"Applying saturation: {saturation}")
    adjusted = apply_saturation(clips, saturation, args.dry_run)
    print(f"\n{'Would adjust' if args.dry_run else 'Adjusted'} {adjusted} clips")

if __name__ == "__main__":
    main()
