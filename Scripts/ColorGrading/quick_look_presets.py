#!/usr/bin/env python3
"""
Quick Look Presets Library for DaVinci Resolve

Apply professional cinematic looks with one command.

Usage:
    python3 quick_look_presets.py --look netflix --all
    python3 quick_look_presets.py --look teal-orange --track 1
    python3 quick_look_presets.py --list-looks

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import Dict, Any

api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))

LOOK_PRESETS = {
    'netflix': {
        'name': 'Netflix Look',
        'cdl': {
            'slope': [1.05, 0.98, 0.95, 1.0],
            'offset': [-0.03, -0.02, 0.01, 0.0],
            'power': [0.95, 0.97, 1.0, 1.0],
            'saturation': 1.08
        },
        'desc': 'Warm midtones, deep shadows, slightly desaturated blues'
    },
    'arri-alexa': {
        'name': 'ARRI Alexa Look',
        'cdl': {
            'slope': [1.0, 1.0, 1.0, 1.0],
            'offset': [0.0, 0.0, 0.0, 0.0],
            'power': [1.0, 1.0, 1.0, 1.0],
            'saturation': 0.95
        },
        'desc': 'Clean, natural, slightly desaturated'
    },
    'teal-orange': {
        'name': 'Cinematic Teal & Orange',
        'cdl': {
            'slope': [1.1, 0.98, 0.92, 1.0],
            'offset': [0.02, 0.0, 0.05, 0.0],
            'power': [0.9, 0.95, 1.05, 1.0],
            'saturation': 1.2
        },
        'desc': 'Hollywood blockbuster standard'
    },
    'kodak-5219': {
        'name': 'Kodak Vision3 5219',
        'cdl': {
            'slope': [1.02, 1.0, 0.98, 1.0],
            'offset': [0.01, 0.0, 0.02, 0.0],
            'power': [0.92, 0.95, 0.98, 1.0],
            'saturation': 1.05
        },
        'desc': 'Film stock emulation - warm, contrasty'
    },
    'documentary': {
        'name': 'Documentary Style',
        'cdl': {
            'slope': [1.0, 1.0, 1.0, 1.0],
            'offset': [0.0, 0.0, 0.0, 0.0],
            'power': [1.05, 1.05, 1.05, 1.0],
            'saturation': 0.9
        },
        'desc': 'Low contrast, natural colors'
    },
    'music-video': {
        'name': 'Music Video Look',
        'cdl': {
            'slope': [1.15, 1.1, 1.05, 1.0],
            'offset': [0.0, 0.0, 0.0, 0.0],
            'power': [0.75, 0.8, 0.85, 1.0],
            'saturation': 1.4
        },
        'desc': 'High saturation, strong contrast'
    },
    'bleach-bypass': {
        'name': 'Bleach Bypass',
        'cdl': {
            'slope': [1.1, 1.1, 1.1, 1.0],
            'offset': [0.0, 0.0, 0.0, 0.0],
            'power': [0.85, 0.85, 0.85, 1.0],
            'saturation': 0.5
        },
        'desc': 'Desaturated, high contrast, gritty'
    },
    'vintage': {
        'name': 'Vintage Film',
        'cdl': {
            'slope': [1.05, 1.0, 0.95, 1.0],
            'offset': [0.05, 0.03, 0.02, 0.0],
            'power': [0.98, 0.98, 1.02, 1.0],
            'saturation': 0.85
        },
        'desc': 'Faded, warm, nostalgic'
    },
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

def apply_look(clip, cdl_data):
    try:
        return clip.SetNodeColorData(1, cdl_data)
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Quick Look Presets")
    parser.add_argument('--look', choices=LOOK_PRESETS.keys(), help='Look preset to apply')
    parser.add_argument('--list-looks', action='store_true', help='List available looks')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--track', type=int)
    parser.add_argument('--color', type=str)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.list_looks:
        print("=" * 70)
        print("Available Quick Looks")
        print("=" * 70)
        for key, data in LOOK_PRESETS.items():
            print(f"\n{key}:")
            print(f"  {data['name']}")
            print(f"  {data['desc']}")
        return

    if not args.look:
        parser.print_help()
        return

    if not args.all and not args.track and not args.color:
        print("Error: Specify target")
        sys.exit(1)

    print(f"Applying look: {LOOK_PRESETS[args.look]['name']}")

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

    cdl = LOOK_PRESETS[args.look]['cdl']
    applied = 0
    for clip in clips:
        if args.dry_run:
            print(f"  Would apply to: {clip.GetName()}")
            applied += 1
        else:
            if apply_look(clip, cdl):
                print(f"  ✅ {clip.GetName()}")
                applied += 1
    print(f"\n{applied} clips processed")

if __name__ == "__main__":
    main()
