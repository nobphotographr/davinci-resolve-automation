#!/usr/bin/env python3
"""
Deliverables Checklist Generator for DaVinci Resolve

Generate comprehensive deliverables checklist for project delivery,
including render settings verification, file format checks, and
quality assurance items.

Usage:
    # Generate checklist for current project
    python3 deliverables_checklist.py --output checklist.md

    # Generate with custom template
    python3 deliverables_checklist.py --template broadcast --output checklist.md

    # Quick project status check
    python3 deliverables_checklist.py --quick-check

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import argparse
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Checklist templates
CHECKLIST_TEMPLATES = {
    'broadcast': {
        'name': 'Broadcast Delivery',
        'categories': [
            'Technical Specifications',
            'Video Quality',
            'Audio Quality',
            'Timecode & Metadata',
            'File Delivery',
        ]
    },
    'web': {
        'name': 'Web/Social Media Delivery',
        'categories': [
            'Format & Resolution',
            'Compression Settings',
            'Audio Mix',
            'Subtitles/Captions',
            'File Organization',
        ]
    },
    'cinema': {
        'name': 'Cinema DCP Delivery',
        'categories': [
            'DCP Specifications',
            'Color Space',
            'Audio Channels',
            'Subtitles',
            'QC Checks',
        ]
    },
    'archive': {
        'name': 'Archive/Master Delivery',
        'categories': [
            'Master File Formats',
            'Backup Verification',
            'Project Files',
            'Documentation',
            'Long-term Storage',
        ]
    },
}


def get_project_info(project) -> Dict[str, Any]:
    """
    Get project information.

    Args:
        project: Project object

    Returns:
        Dictionary with project info
    """
    info = {
        'name': project.GetName(),
        'timeline_count': project.GetTimelineCount(),
        'timelines': [],
    }

    # Get timeline information
    for i in range(1, info['timeline_count'] + 1):
        timeline = project.GetTimelineByIndex(i)
        if timeline:
            try:
                tl_info = {
                    'name': timeline.GetName(),
                    'fps': timeline.GetSetting('timelineFrameRate'),
                    'resolution_width': timeline.GetSetting('timelineResolutionWidth'),
                    'resolution_height': timeline.GetSetting('timelineResolutionHeight'),
                    'start_timecode': timeline.GetStartTimecode(),
                }
                info['timelines'].append(tl_info)
            except:
                info['timelines'].append({
                    'name': timeline.GetName(),
                    'error': 'Could not retrieve settings'
                })

    return info


def get_render_settings(project) -> Dict[str, Any]:
    """
    Get current render settings.

    Args:
        project: Project object

    Returns:
        Dictionary with render settings
    """
    settings = {
        'available': False,
    }

    try:
        # Note: Render settings access may be limited in API
        # Typically accessed through render queue
        current_render_format = project.GetCurrentRenderFormatAndCodec()

        if current_render_format:
            settings['available'] = True
            settings['format'] = current_render_format.get('format', 'Unknown')
            settings['codec'] = current_render_format.get('codec', 'Unknown')

    except:
        pass

    return settings


def generate_broadcast_checklist(project_info: Dict[str, Any]) -> List[str]:
    """Generate broadcast delivery checklist items."""
    items = []

    # Technical Specifications
    items.append("## Technical Specifications\n")
    items.append("- [ ] Video format matches delivery specs (resolution, frame rate, codec)")
    items.append("- [ ] Color space correctly set (Rec.709 for HD, Rec.2020 for UHD)")
    items.append("- [ ] Bit depth verified (8-bit/10-bit as required)")
    items.append("- [ ] Aspect ratio correct (16:9, 4:3, etc.)")
    items.append("- [ ] Interlaced/Progressive setting verified\n")

    # Video Quality
    items.append("## Video Quality\n")
    items.append("- [ ] No dropped frames")
    items.append("- [ ] No frozen frames")
    items.append("- [ ] No visible compression artifacts")
    items.append("- [ ] Blacks are legal (16 on 8-bit scale)")
    items.append("- [ ] Whites are legal (235 on 8-bit scale)")
    items.append("- [ ] No illegal colors (chroma levels checked)")
    items.append("- [ ] Safe action/title areas respected\n")

    # Audio Quality
    items.append("## Audio Quality\n")
    items.append("- [ ] Audio levels meet broadcast standards (-23 LUFS for EBU R128)")
    items.append("- [ ] No audio clipping or distortion")
    items.append("- [ ] Stereo/5.1 channels correctly mapped")
    items.append("- [ ] Audio sync verified throughout")
    items.append("- [ ] Tone and bars included (if required)")
    items.append("- [ ] Silence at head/tail as specified\n")

    # Timecode & Metadata
    items.append("## Timecode & Metadata\n")
    items.append("- [ ] Timecode starts at specified time")
    items.append("- [ ] Timecode is continuous (no breaks)")
    items.append("- [ ] Metadata embedded (title, episode, date, etc.)")
    items.append("- [ ] Closed captions/subtitles verified (if applicable)\n")

    # File Delivery
    items.append("## File Delivery\n")
    items.append("- [ ] File naming convention followed")
    items.append("- [ ] All required versions rendered (master, proxy, etc.)")
    items.append("- [ ] Checksums/MD5 hashes generated")
    items.append("- [ ] Files uploaded to delivery platform")
    items.append("- [ ] Backup copies created\n")

    return items


def generate_web_checklist(project_info: Dict[str, Any]) -> List[str]:
    """Generate web/social media delivery checklist items."""
    items = []

    items.append("## Format & Resolution\n")
    items.append("- [ ] Resolution matches platform requirements")
    items.append("- [ ] Aspect ratio correct (16:9, 9:16, 1:1, 4:5)")
    items.append("- [ ] Frame rate appropriate (23.976, 24, 25, 29.97, 30, 60)")
    items.append("- [ ] File format compatible (MP4, MOV, etc.)\n")

    items.append("## Compression Settings\n")
    items.append("- [ ] H.264/H.265 codec used")
    items.append("- [ ] Bitrate optimized for platform")
    items.append("- [ ] File size within platform limits")
    items.append("- [ ] Quality acceptable after compression\n")

    items.append("## Audio Mix\n")
    items.append("- [ ] Audio normalized for platform")
    items.append("- [ ] Stereo downmix from 5.1 (if applicable)")
    items.append("- [ ] Dialogue clearly audible")
    items.append("- [ ] Music and SFX balanced\n")

    items.append("## Subtitles/Captions\n")
    items.append("- [ ] Burned-in subtitles (if required)")
    items.append("- [ ] SRT file exported (if required)")
    items.append("- [ ] Caption accuracy verified")
    items.append("- [ ] Safe title area respected\n")

    items.append("## File Organization\n")
    items.append("- [ ] Files named according to platform")
    items.append("- [ ] Thumbnails/poster frames exported")
    items.append("- [ ] Multiple versions prepared (1080p, 720p, 480p)")
    items.append("- [ ] Upload tested on target platform\n")

    return items


def generate_cinema_checklist(project_info: Dict[str, Any]) -> List[str]:
    """Generate cinema DCP delivery checklist items."""
    items = []

    items.append("## DCP Specifications\n")
    items.append("- [ ] DCP package created (2K or 4K)")
    items.append("- [ ] Frame rate correct (24fps for cinema)")
    items.append("- [ ] JPEG2000 compression verified")
    items.append("- [ ] Interop or SMPTE DCP as specified")
    items.append("- [ ] Encryption applied (if required)\n")

    items.append("## Color Space\n")
    items.append("- [ ] Color graded in P3-D65 color space")
    items.append("- [ ] Color calibration verified on DCI projector")
    items.append("- [ ] No color banding or posterization")
    items.append("- [ ] Black levels and contrast checked\n")

    items.append("## Audio Channels\n")
    items.append("- [ ] 5.1 or 7.1 surround mix")
    items.append("- [ ] Audio format PCM 24-bit 48kHz")
    items.append("- [ ] Channel mapping verified")
    items.append("- [ ] Reference level calibrated to 85dB SPL\n")

    items.append("## Subtitles\n")
    items.append("- [ ] Subtitle track included (if required)")
    items.append("- [ ] Multiple language versions prepared")
    items.append("- [ ] Subtitle positioning correct")
    items.append("- [ ] Timing verified\n")

    items.append("## QC Checks\n")
    items.append("- [ ] DCP played back on certified server")
    items.append("- [ ] Complete package integrity verified")
    items.append("- [ ] CPL and PKL files checked")
    items.append("- [ ] Test screening completed")
    items.append("- [ ] Hard drive formatted correctly (ext2/ext3)\n")

    return items


def generate_archive_checklist(project_info: Dict[str, Any]) -> List[str]:
    """Generate archive/master delivery checklist items."""
    items = []

    items.append("## Master File Formats\n")
    items.append("- [ ] Uncompressed or lossless codec (ProRes, DNxHD)")
    items.append("- [ ] Full resolution preserved")
    items.append("- [ ] Highest quality settings used")
    items.append("- [ ] Alpha channel included (if applicable)")
    items.append("- [ ] Timecode embedded\n")

    items.append("## Backup Verification\n")
    items.append("- [ ] Multiple backup copies created (minimum 2)")
    items.append("- [ ] Backups on different media types")
    items.append("- [ ] File integrity verified (checksums)")
    items.append("- [ ] Backup location documented")
    items.append("- [ ] Restore test performed\n")

    items.append("## Project Files\n")
    items.append("- [ ] DaVinci Resolve project exported (.drp)")
    items.append("- [ ] All source media included/catalogued")
    items.append("- [ ] LUTs and color correction data exported")
    items.append("- [ ] Fonts and graphics assets included")
    items.append("- [ ] Project structure documented\n")

    items.append("## Documentation\n")
    items.append("- [ ] Shot list/EDL exported")
    items.append("- [ ] Technical specifications document")
    items.append("- [ ] Credits and metadata document")
    items.append("- [ ] Color grading notes")
    items.append("- [ ] Audio mix notes\n")

    items.append("## Long-term Storage\n")
    items.append("- [ ] Archive media labeled clearly")
    items.append("- [ ] Storage location recorded")
    items.append("- [ ] Retrieval process documented")
    items.append("- [ ] Periodic integrity checks scheduled")
    items.append("- [ ] Migration plan for obsolete formats\n")

    return items


def generate_checklist(
    project_info: Dict[str, Any],
    template: str,
    output_path: str
) -> bool:
    """
    Generate deliverables checklist.

    Args:
        project_info: Project information
        template: Template name
        output_path: Output file path

    Returns:
        True if successful
    """
    try:
        template_info = CHECKLIST_TEMPLATES[template]

        with open(output_path, 'w') as f:
            # Header
            f.write(f"# Deliverables Checklist: {template_info['name']}\n\n")
            f.write(f"**Project:** {project_info['name']}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Project info
            f.write("## Project Information\n\n")
            f.write(f"- **Project Name:** {project_info['name']}\n")
            f.write(f"- **Timeline Count:** {project_info['timeline_count']}\n\n")

            if project_info['timelines']:
                f.write("**Timelines:**\n\n")
                for tl in project_info['timelines']:
                    f.write(f"- {tl['name']}\n")
                    if 'fps' in tl:
                        f.write(f"  - FPS: {tl.get('fps', 'N/A')}\n")
                        f.write(f"  - Resolution: {tl.get('resolution_width', 'N/A')}x{tl.get('resolution_height', 'N/A')}\n")
                f.write("\n")

            f.write("---\n\n")

            # Checklist items
            if template == 'broadcast':
                items = generate_broadcast_checklist(project_info)
            elif template == 'web':
                items = generate_web_checklist(project_info)
            elif template == 'cinema':
                items = generate_cinema_checklist(project_info)
            elif template == 'archive':
                items = generate_archive_checklist(project_info)
            else:
                items = generate_broadcast_checklist(project_info)

            for item in items:
                f.write(item)

            # Footer
            f.write("\n---\n\n")
            f.write("## Sign-off\n\n")
            f.write("- **Completed by:** ___________________________\n")
            f.write("- **Date:** ___________________________\n")
            f.write("- **Approved by:** ___________________________\n")
            f.write("- **Date:** ___________________________\n")

        return True

    except Exception as e:
        print(f"Error generating checklist: {e}")
        return False


def quick_check(project) -> None:
    """
    Perform quick project status check.

    Args:
        project: Project object
    """
    print("Quick Project Status Check")
    print("=" * 70)
    print()

    info = get_project_info(project)

    print(f"Project: {info['name']}")
    print(f"Timelines: {info['timeline_count']}")
    print()

    if info['timelines']:
        print("Timeline Details:")
        for tl in info['timelines']:
            print(f"  • {tl['name']}")
            if 'fps' in tl:
                print(f"    FPS: {tl.get('fps', 'N/A')}")
                print(f"    Resolution: {tl.get('resolution_width', 'N/A')}x{tl.get('resolution_height', 'N/A')}")
            if tl.get('error'):
                print(f"    ⚠️  {tl['error']}")
        print()

    # Check render settings
    render_settings = get_render_settings(project)

    print("Render Settings:")
    if render_settings['available']:
        print(f"  Format: {render_settings.get('format', 'Unknown')}")
        print(f"  Codec: {render_settings.get('codec', 'Unknown')}")
    else:
        print("  ⚠️  Render settings not accessible via API")
        print("  Check in Deliver page manually")
    print()

    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate deliverables checklist for DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate broadcast delivery checklist
  %(prog)s --template broadcast --output checklist.md

  # Generate web delivery checklist
  %(prog)s --template web --output web_checklist.md

  # Quick project status check
  %(prog)s --quick-check

  # List available templates
  %(prog)s --list-templates

Templates:
  - broadcast: Broadcast/TV delivery
  - web: Web/social media delivery
  - cinema: Cinema DCP delivery
  - archive: Archive/master delivery
        """
    )

    # Operation mode
    mode_group = parser.add_mutually_exclusive_group(required=True)

    mode_group.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Output checklist file (Markdown)'
    )

    mode_group.add_argument(
        '--quick-check',
        action='store_true',
        help='Quick project status check'
    )

    mode_group.add_argument(
        '--list-templates',
        action='store_true',
        help='List available checklist templates'
    )

    # Template selection
    parser.add_argument(
        '--template',
        type=str,
        choices=list(CHECKLIST_TEMPLATES.keys()),
        default='broadcast',
        help='Checklist template (default: broadcast)'
    )

    args = parser.parse_args()

    # List templates
    if args.list_templates:
        print("=" * 70)
        print("Available Checklist Templates")
        print("=" * 70)
        print()

        for key, template in CHECKLIST_TEMPLATES.items():
            print(f"{key}:")
            print(f"  {template['name']}")
            print(f"  Categories: {', '.join(template['categories'])}")
            print()

        return

    print("=" * 70)
    print("DaVinci Resolve Deliverables Checklist Generator")
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

        print(f"✅ Connected to project: {project.GetName()}")
        print()

    except ImportError:
        print("❌ DaVinci Resolve Python API not available")
        print("   Check RESOLVE_SCRIPT_API environment variable")
        sys.exit(1)

    # Execute operation
    if args.quick_check:
        quick_check(project)

    elif args.output:
        print(f"Generating {CHECKLIST_TEMPLATES[args.template]['name']} checklist...")
        print()

        project_info = get_project_info(project)
        success = generate_checklist(project_info, args.template, args.output)

        print()
        print("=" * 70)

        if success:
            print(f"✅ Successfully generated checklist: {args.output}")
            print(f"   Template: {CHECKLIST_TEMPLATES[args.template]['name']}")
        else:
            print("❌ Checklist generation failed")

        print("=" * 70)


if __name__ == "__main__":
    main()
