#!/usr/bin/env python3
"""
Contrast & Dynamic Range Manager for DaVinci Resolve

Batch adjust contrast with S-curve, highlight compression, shadow lift.

Usage:
    python3 contrast_manager.py --preset cinematic --all
    python3 contrast_manager.py --contrast 1.2 --track 1
    python3 contrast_manager.py --highlights -0.2 --shadows 0.1 --all

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Optional

api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))

CONTRAST_PRESETS = {
    'flat': {'power': [1.0, 1.0, 1.0, 1.0], 'desc': 'Flat contrast'},
    'natural': {'power': [0.95, 0.95, 0.95, 1.0], 'desc': 'Natural contrast'},
    'cinematic': {'power': [0.85, 0.85, 0.85, 1.0], 'desc': 'Cinematic S-curve'},
    'high': {'power': [0.7, 0.7, 0.7, 1.0], 'desc': 'High contrast'},
}

def get_clips(timeline, all_clips=False, track=None, color=None):
    clips = []
    for i in range(1, timeline.GetTrackCount('video') + 1):
        if track and i != track:
            continue
        items = timeline.GetItemListInTrack('video', i)
        if items:
            for item in items:
                if color and (not item.GetClipColor() or item.GetClipColor().lower() != color.lower()):
                    continue
                clips.append(item)
    return clips

def adjust_contrast(clip, power_values=None, highlights=None, shadows=None):
    try:
        cdl = clip.GetNodeColorData(1) or {'slope': [1.0]*4, 'offset': [0.0]*4, 'power': [1.0]*4, 'saturation': 1.0}
        if power_values:
            cdl['power'] = power_values
        if highlights:
            for i in range(3):
                cdl['slope'][i] = 1.0 + highlights
        if shadows:
            for i in range(3):
                cdl['offset'][i] = shadows
        return clip.SetNodeColorData(1, cdl)
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Contrast manager")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preset', choices=CONTRAST_PRESETS.keys())
    mode.add_argument('--contrast', type=float)
    mode.add_argument('--list-presets', action='store_true')

    parser.add_argument('--highlights', type=float)
    parser.add_argument('--shadows', type=float)
    target = parser.add_mutually_exclusive_group()
    target.add_argument('--all', action='store_true')
    target.add_argument('--track', type=int)
    target.add_argument('--color', type=str)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.list_presets:
        for name, data in CONTRAST_PRESETS.items():
            print(f"{name}: {data['desc']}")
        return

    if not args.all and not args.track and not args.color and not args.list_presets:
        print("Error: Specify target")
        sys.exit(1)

    try:
        import DaVinciResolveScript as dvr
        timeline = dvr.scriptapp("Resolve").GetProjectManager().GetCurrentProject().GetCurrentTimeline()
        if not timeline:
            print("❌ No timeline")
            sys.exit(1)
    except:
        print("❌ Connection failed")
        sys.exit(1)

    clips = get_clips(timeline, args.all, args.track, args.color)
    if not clips:
        print("❌ No clips")
        sys.exit(1)

    power = CONTRAST_PRESETS[args.preset]['power'] if args.preset else None
    adjusted = 0
    for clip in clips:
        if args.dry_run:
            print(f"  Would adjust: {clip.GetName()}")
            adjusted += 1
        else:
            if adjust_contrast(clip, power, args.highlights, args.shadows):
                print(f"  ✅ {clip.GetName()}")
                adjusted += 1
    print(f"\n{adjusted} clips adjusted")

if __name__ == "__main__":
    main()
