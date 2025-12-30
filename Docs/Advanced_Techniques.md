# Advanced Techniques for DaVinci Resolve Automation

## Overview

This document covers advanced techniques and workarounds discovered by the community. Many of these are not documented in the official API reference.

## Timeline Item Selection Workaround

### Problem

**API Limitation**: No native method to get selected timeline clips.

```python
# This doesn't exist
selected_items = timeline.GetSelectedItems()  # ❌ No such method
```

### Solution: Clip Color as Selection Marker

Use clip color as a temporary selection indicator.

**Workflow**:
1. User manually selects clips in timeline
2. User right-clicks → Clip Color → Orange (or any specific color)
3. Script filters clips by that color

**Implementation**:

```python
def get_clips_by_color(timeline, color_name="Orange"):
    """
    Get all timeline clips with specified color.

    Args:
        timeline: Timeline object
        color_name: Color name (e.g., "Orange", "Blue", "Green")

    Returns:
        List of TimelineItem objects
    """
    selected_items = []

    # Check video tracks
    video_track_count = timeline.GetTrackCount("video")
    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack("video", track_index)
        for item in items:
            if item.GetClipColor() == color_name:
                selected_items.append(item)

    # Check audio tracks
    audio_track_count = timeline.GetTrackCount("audio")
    for track_index in range(1, audio_track_count + 1):
        items = timeline.GetItemListInTrack("audio", track_index)
        for item in items:
            if item.GetClipColor() == color_name:
                selected_items.append(item)

    return selected_items
```

**Usage**:

```python
# 1. User selects clips and assigns Orange color via UI
# 2. Script retrieves them
timeline = project.GetCurrentTimeline()
selected_clips = get_clips_by_color(timeline, "Orange")

print(f"Found {len(selected_clips)} clips with Orange color")

# Process selected clips
for clip in selected_clips:
    # Apply DRX, LUT, etc.
    clip.SetLUT(1, "my_lut.cube")

# 3. Optional: Reset color after processing
for clip in selected_clips:
    clip.ClearClipColor()
```

### Important Limitations

**Clip Color Compatibility**:
- ✅ Standard video/audio clips
- ❌ Some effect templates (without Fusion support)
- ❌ Subtitle clips

**Workflow Conflicts**:
- May interfere if you already use clip colors for organization
- Alternative: Use enabled/disabled state instead

```python
# Alternative: Use enabled/disabled state
def get_disabled_clips(timeline):
    """Get all disabled clips (alternative selection marker)"""
    disabled_items = []

    for track_type in ["video", "audio"]:
        track_count = timeline.GetTrackCount(track_type)
        for i in range(1, track_count + 1):
            items = timeline.GetItemListInTrack(track_type, i)
            for item in items:
                if not item.GetClipEnabled():
                    disabled_items.append(item)

    return disabled_items
```

**Note**: Disabled clips won't render, which may not be ideal.

### Best Practices

1. **Document the workflow** - Tell users to apply specific color before running script
2. **Validate selection** - Check if any clips were found:

```python
if not selected_clips:
    print("❌ No clips with Orange color found")
    print("Please select clips and apply Orange color via right-click menu")
    sys.exit(1)
```

3. **Clear color after processing** - Prevent interference with next operation:

```python
for clip in selected_clips:
    clip.ClearClipColor()
```

4. **Use unique color** - Choose a color unlikely to be used for other purposes

## Track Iteration Patterns

### Iterate All Tracks and Clips

```python
def iterate_all_clips(timeline):
    """Iterate through all clips in timeline"""
    for track_type in ["video", "audio"]:
        track_count = timeline.GetTrackCount(track_type)
        print(f"{track_type.capitalize()} tracks: {track_count}")

        for track_index in range(1, track_count + 1):
            items = timeline.GetItemListInTrack(track_type, track_index)
            print(f"  Track {track_index}: {len(items)} clips")

            for item in items:
                name = item.GetName()
                duration = item.GetDuration()
                print(f"    - {name} ({duration} frames)")
```

### Process Specific Track

```python
# Video track 1 only
video_items = timeline.GetItemListInTrack("video", 1)

for item in video_items:
    # Process each clip
    pass
```

### Filter by Clip Properties

```python
def get_clips_by_name_pattern(timeline, pattern):
    """Get clips matching name pattern"""
    import re
    matching_clips = []

    for track_type in ["video", "audio"]:
        track_count = timeline.GetTrackCount(track_type)
        for i in range(1, track_count + 1):
            items = timeline.GetItemListInTrack(track_type, i)
            for item in items:
                if re.search(pattern, item.GetName()):
                    matching_clips.append(item)

    return matching_clips

# Example: Get all BRAW clips
braw_clips = get_clips_by_name_pattern(timeline, r"\.braw$")
```

## Batch Operations on Filtered Clips

### Example: Apply LUT to Specific Clips

```python
def batch_apply_lut_by_color(timeline, color_name, lut_filename, node_index=1):
    """
    Apply LUT to all clips with specific color.

    Args:
        timeline: Timeline object
        color_name: Clip color to filter (e.g., "Orange")
        lut_filename: LUT filename (must be in LUT directory)
        node_index: Node index to apply LUT (1-based)
    """
    # Get clips by color
    clips = get_clips_by_color(timeline, color_name)

    if not clips:
        print(f"⚠️  No clips with {color_name} color found")
        return 0

    print(f"Found {len(clips)} clips with {color_name} color")

    # Apply LUT to each clip
    success_count = 0
    for clip in clips:
        success = clip.SetLUT(node_index, lut_filename)
        if success:
            success_count += 1
            print(f"  ✅ {clip.GetName()}")
        else:
            print(f"  ❌ {clip.GetName()}")

    print(f"\nApplied LUT to {success_count}/{len(clips)} clips")
    return success_count

# Usage
project.RefreshLUTList()
batch_apply_lut_by_color(timeline, "Orange", "Classic_Cinema_Custom.cube", 4)
```

### Example: Apply DRX Template to Selected Clips

```python
def batch_apply_drx_by_color(timeline, color_name, drx_path):
    """Apply DRX template to clips with specific color"""
    clips = get_clips_by_color(timeline, color_name)

    if not clips:
        print(f"⚠️  No clips with {color_name} color found")
        return 0

    success_count = 0
    for clip in clips:
        graph = clip.GetNodeGraph()
        success = graph.ApplyGradeFromDRX(drx_path, 0)
        if success:
            success_count += 1
            print(f"  ✅ {clip.GetName()}")

    print(f"\nApplied DRX to {success_count}/{len(clips)} clips")
    return success_count
```

## Timeline Property Inspection

### Get Timeline Information

```python
def inspect_timeline(timeline):
    """Print detailed timeline information"""
    print("=" * 70)
    print(f"Timeline: {timeline.GetName()}")
    print("=" * 70)

    # Basic info
    start_frame = timeline.GetStartFrame()
    end_frame = timeline.GetEndFrame()
    print(f"\nFrame range: {start_frame} - {end_frame}")

    # Track counts
    video_tracks = timeline.GetTrackCount("video")
    audio_tracks = timeline.GetTrackCount("audio")
    print(f"\nVideo tracks: {video_tracks}")
    print(f"Audio tracks: {audio_tracks}")

    # Current marker info
    markers = timeline.GetMarkers()
    print(f"\nMarkers: {len(markers)}")

    # Current playhead position
    current_frame = timeline.GetCurrentVideoItem()
    if current_frame:
        print(f"Current item: {current_frame.GetName()}")
```

## Fusion Page Integration Notes

### Important Context

The articles by hitsugi_yukana cover **Fusion page** scripting extensively. Key points:

1. **Fusion-specific features** (right-click menus, custom controls) are **not available** in Color page
2. **Fusion scripts use .fu files** placed in `Config/` directory (macOS/Windows paths differ)
3. **Python API** focuses on Project/Timeline/Color management, not Fusion compositing

### Fusion vs Python API

| Feature | Fusion Page (.fu scripts) | Python API |
|---------|---------------------------|------------|
| Custom menus | ✅ | ❌ |
| UI controls | ✅ (HTML, ComboBox, etc.) | ❌ |
| Node manipulation | ✅ (Full control) | ❌ (Limited) |
| Project management | Limited | ✅ |
| Timeline operations | Limited | ✅ |
| Color grading | Via nodes only | ✅ (CDL, LUT) |

### When to Use Each

**Use Fusion Page Scripts** when:
- Building custom UI tools
- Manipulating Fusion composition nodes
- Creating interactive controls

**Use Python API** when:
- Automating project setup
- Batch timeline operations
- Applying color grades/LUTs
- Rendering workflows

## Cross-Platform Considerations

### Config File Paths

Different OS locations for custom scripts:

**macOS**:
```
~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Config/
```

**Windows**:
```
C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Config\
```

**Linux**:
```
~/.local/share/DaVinciResolve/Fusion/Config/
```

### Language-Specific Issues

**Menu item references** must match UI language:
- English: `Animate`
- Japanese: `アニメート`

**Workaround**: Use language-agnostic approaches (object types instead of menu names)

## Resources and Credits

These advanced techniques were discovered and documented by:
- **hitsugi_yukana** - Extensive Fusion page scripting articles (Japanese)
  - [Context Menu Implementation](https://zenn.dev/hitsugi_yukana/articles/32a4463170c0d3)
  - [ComboBox String Retrieval](https://zenn.dev/hitsugi_yukana/articles/ef2c4067708d90)
  - [Inspector HTML Display](https://zenn.dev/hitsugi_yukana/articles/fusion_inspector_html)
  - [Control Change Handlers](https://zenn.dev/hitsugi_yukana/articles/hy_usercontrol_executeonchanged)
  - [Selected Timeline Items Workaround](https://zenn.dev/hitsugi_yukana/articles/hy_alternative_getselected-timelineitem)

## Future Improvements

Potential API additions to request from Blackmagic Design:
- `timeline.GetSelectedItems()` - Native selection API
- `timeline_item.AddNode()` - Programmatic node creation
- `timeline_item.SetPrimaryWheels()` - Direct wheel control
- Better cross-page scripting support
