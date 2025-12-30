#!/usr/bin/env python3
"""
Render Queue Manager for DaVinci Resolve

Manage render jobs, monitor progress, and batch render with presets.

Usage:
    # Show render queue status
    python3 render_manager.py --status

    # Add render job with preset
    python3 render_manager.py --add --preset prores422hq --output ~/renders/

    # Start rendering and monitor progress
    python3 render_manager.py --start --monitor

    # Clear completed jobs
    python3 render_manager.py --clear-completed

    # List available presets
    python3 render_manager.py --list-presets

Author: DaVinci Resolve Automation Project
License: MIT
"""

import sys
import os
import time
import argparse
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add DaVinci Resolve API to path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(os.path.join(api_path, "Modules"))


# Render presets
RENDER_PRESETS = {
    'prores422hq': {
        'format': 'QuickTime',
        'codec': 'ProRes422HQ',
        'description': 'ProRes 422 HQ - High quality for editing'
    },
    'prores422': {
        'format': 'QuickTime',
        'codec': 'ProRes422',
        'description': 'ProRes 422 - Standard quality'
    },
    'prores4444': {
        'format': 'QuickTime',
        'codec': 'ProRes4444',
        'description': 'ProRes 4444 - Alpha channel support'
    },
    'h264_high': {
        'format': 'mp4',
        'codec': 'H264',
        'description': 'H.264 High Quality - Web/streaming'
    },
    'h265_high': {
        'format': 'mp4',
        'codec': 'H265',
        'description': 'H.265/HEVC High Quality - Efficient compression'
    },
    'dnxhr_hqx': {
        'format': 'mxf',
        'codec': 'DNxHRHQX',
        'description': 'DNxHR HQX - High quality for post'
    },
    'dnxhr_sq': {
        'format': 'mxf',
        'codec': 'DNxHRSQ',
        'description': 'DNxHR SQ - Standard quality'
    }
}


def list_presets():
    """Display available render presets."""
    print("=" * 70)
    print("Available Render Presets")
    print("=" * 70)
    print()

    for preset_name, preset_info in RENDER_PRESETS.items():
        print(f"📦 {preset_name}")
        print(f"   Format: {preset_info['format']}")
        print(f"   Codec: {preset_info['codec']}")
        print(f"   Description: {preset_info['description']}")
        print()


def get_render_job_status(job) -> Dict[str, Any]:
    """
    Get render job status information.

    Args:
        job: Render job object

    Returns:
        Dictionary with job status
    """
    try:
        status = {
            'render_job_id': job.GetJobId() if hasattr(job, 'GetJobId') else 'Unknown',
            'status': job.GetStatus() if hasattr(job, 'GetStatus') else 'Unknown',
            'completion_percent': 0,
            'time_remaining': 'Unknown'
        }

        # Try to get completion percentage
        if hasattr(job, 'GetCompletionPercentage'):
            status['completion_percent'] = job.GetCompletionPercentage()

        # Try to get time remaining
        if hasattr(job, 'GetTimeRemaining'):
            status['time_remaining'] = job.GetTimeRemaining()

        return status

    except Exception as e:
        return {
            'render_job_id': 'Unknown',
            'status': 'Error',
            'completion_percent': 0,
            'time_remaining': 'Unknown',
            'error': str(e)
        }


def format_time_remaining(seconds: int) -> str:
    """
    Format seconds into human-readable time.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if seconds < 0:
        return "Unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def show_render_queue_status(project):
    """
    Display current render queue status.

    Args:
        project: Project object
    """
    print("=" * 70)
    print("Render Queue Status")
    print("=" * 70)
    print()

    # Get render jobs
    render_job_list = project.GetRenderJobList()

    if not render_job_list:
        print("📭 Render queue is empty")
        print()
        return

    print(f"Total Jobs: {len(render_job_list)}")
    print()

    for i, job in enumerate(render_job_list, 1):
        job_id = job.get('JobId', 'Unknown')
        target_dir = job.get('TargetDir', 'Unknown')
        render_preset = job.get('RenderPresetName', 'Unknown')
        job_status = job.get('JobStatus', 'Unknown')

        print(f"{i}. Job ID: {job_id}")
        print(f"   Status: {job_status}")
        print(f"   Preset: {render_preset}")
        print(f"   Output: {target_dir}")

        # Show completion if rendering
        if job_status == "Rendering":
            completion = job.get('CompletionPercentage', 0)
            print(f"   Progress: {completion}%")

        print()

    print("=" * 70)


def add_render_job(
    project,
    preset_name: Optional[str] = None,
    output_dir: Optional[str] = None,
    custom_settings: Optional[Dict] = None
) -> bool:
    """
    Add a render job to the queue.

    Args:
        project: Project object
        preset_name: Preset name from RENDER_PRESETS
        output_dir: Output directory path
        custom_settings: Custom render settings dictionary

    Returns:
        True if job added successfully
    """
    timeline = project.GetCurrentTimeline()

    if not timeline:
        print("❌ No timeline is open")
        return False

    # Use preset or custom settings
    if preset_name:
        if preset_name not in RENDER_PRESETS:
            print(f"❌ Unknown preset: {preset_name}")
            print(f"   Available presets: {', '.join(RENDER_PRESETS.keys())}")
            return False

        preset = RENDER_PRESETS[preset_name]
        render_settings = {
            'SelectAllFrames': True,
            'TargetDir': output_dir or os.path.expanduser('~/Desktop'),
            'CustomName': timeline.GetName(),
            'ExportVideo': True,
            'ExportAudio': True
        }

        # Add format and codec from preset
        if 'format' in preset:
            render_settings['Format'] = preset['format']
        if 'codec' in preset:
            render_settings['Codec'] = preset['codec']

        print(f"Adding render job with preset: {preset_name}")
        print(f"  Format: {preset['format']}")
        print(f"  Codec: {preset['codec']}")

    elif custom_settings:
        render_settings = custom_settings
        print("Adding render job with custom settings")
    else:
        print("❌ Must specify either preset or custom settings")
        return False

    print(f"  Timeline: {timeline.GetName()}")
    print(f"  Output: {render_settings['TargetDir']}")
    print()

    # Add to render queue
    try:
        job_id = project.AddRenderJob()

        if job_id:
            # Set render settings
            project.SetRenderSettings(render_settings)
            print(f"✅ Render job added successfully (ID: {job_id})")
            return True
        else:
            print("❌ Failed to add render job")
            return False

    except Exception as e:
        print(f"❌ Error adding render job: {e}")
        return False


def start_rendering(project, monitor: bool = False) -> bool:
    """
    Start rendering all jobs in queue.

    Args:
        project: Project object
        monitor: Whether to monitor progress

    Returns:
        True if rendering started successfully
    """
    render_job_list = project.GetRenderJobList()

    if not render_job_list:
        print("❌ No jobs in render queue")
        return False

    print("=" * 70)
    print("Starting Render")
    print("=" * 70)
    print()
    print(f"Jobs in queue: {len(render_job_list)}")
    print()

    # Start rendering
    success = project.StartRendering()

    if not success:
        print("❌ Failed to start rendering")
        return False

    print("✅ Rendering started")
    print()

    if monitor:
        monitor_render_progress(project)

    return True


def monitor_render_progress(project):
    """
    Monitor render progress in real-time.

    Args:
        project: Project object
    """
    print("=" * 70)
    print("Monitoring Render Progress")
    print("=" * 70)
    print()
    print("Press Ctrl+C to stop monitoring (rendering will continue)")
    print()

    try:
        last_status = None
        start_time = time.time()

        while True:
            # Check if still rendering
            is_rendering = project.IsRenderingInProgress()

            if not is_rendering:
                elapsed = time.time() - start_time
                print()
                print("=" * 70)
                print(f"✅ Rendering complete! (Total time: {format_time_remaining(int(elapsed))})")
                print("=" * 70)
                break

            # Get current job status
            render_job_list = project.GetRenderJobList()

            if render_job_list:
                current_job = None
                for job in render_job_list:
                    if job.get('JobStatus') == 'Rendering':
                        current_job = job
                        break

                if current_job:
                    job_id = current_job.get('JobId', 'Unknown')
                    completion = current_job.get('CompletionPercentage', 0)

                    # Calculate ETA
                    elapsed = time.time() - start_time
                    if completion > 0:
                        total_estimated = (elapsed / completion) * 100
                        remaining = total_estimated - elapsed
                        eta_str = format_time_remaining(int(remaining))
                    else:
                        eta_str = "Calculating..."

                    status_line = f"Job {job_id}: {completion}% complete | ETA: {eta_str} | Elapsed: {format_time_remaining(int(elapsed))}"

                    # Only print if status changed
                    if status_line != last_status:
                        print(f"\r{status_line}", end='', flush=True)
                        last_status = status_line

            time.sleep(1)

    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Monitoring stopped (rendering continues in background)")
        print()


def clear_completed_jobs(project) -> int:
    """
    Clear completed render jobs from queue.

    Args:
        project: Project object

    Returns:
        Number of jobs cleared
    """
    render_job_list = project.GetRenderJobList()

    if not render_job_list:
        print("📭 Render queue is empty")
        return 0

    cleared_count = 0

    for job in render_job_list:
        job_id = job.get('JobId')
        job_status = job.get('JobStatus')

        if job_status in ['Complete', 'Failed']:
            if project.DeleteRenderJob(job_id):
                print(f"✅ Cleared job {job_id} ({job_status})")
                cleared_count += 1
            else:
                print(f"❌ Failed to clear job {job_id}")

    if cleared_count == 0:
        print("No completed or failed jobs to clear")

    return cleared_count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage DaVinci Resolve render queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current render queue
  %(prog)s --status

  # List available presets
  %(prog)s --list-presets

  # Add job with preset
  %(prog)s --add --preset prores422hq --output ~/renders/

  # Start rendering with progress monitoring
  %(prog)s --start --monitor

  # Clear completed jobs
  %(prog)s --clear-completed
        """
    )

    # Actions
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show render queue status'
    )

    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List available render presets'
    )

    parser.add_argument(
        '--add',
        action='store_true',
        help='Add render job to queue'
    )

    parser.add_argument(
        '--start',
        action='store_true',
        help='Start rendering'
    )

    parser.add_argument(
        '--clear-completed',
        action='store_true',
        help='Clear completed and failed jobs'
    )

    # Options for --add
    parser.add_argument(
        '--preset',
        type=str,
        metavar='NAME',
        help='Render preset name (use --list-presets to see available)'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='DIR',
        help='Output directory (default: ~/Desktop)'
    )

    # Options for --start
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Monitor render progress (use with --start)'
    )

    args = parser.parse_args()

    # List presets (no connection needed)
    if args.list_presets:
        list_presets()
        return

    # For other operations, need connection
    if not any([args.status, args.add, args.start, args.clear_completed]):
        parser.print_help()
        return

    print("=" * 70)
    print("DaVinci Resolve Render Manager")
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

    # Execute actions
    if args.status:
        show_render_queue_status(project)

    if args.add:
        if not args.preset:
            print("❌ --preset is required when using --add")
            print("   Use --list-presets to see available presets")
            sys.exit(1)

        add_render_job(project, args.preset, args.output)

    if args.start:
        start_rendering(project, monitor=args.monitor)

    if args.clear_completed:
        print("Clearing completed jobs...")
        print()
        cleared = clear_completed_jobs(project)
        print()
        print(f"✅ Cleared {cleared} job(s)")


if __name__ == "__main__":
    main()
