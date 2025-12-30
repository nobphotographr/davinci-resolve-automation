# Type Safety and Modern Python Patterns for DaVinci Resolve

## Overview

This document covers modern Python best practices for DaVinci Resolve automation, including type hints, error handling, and clean API wrapper patterns. These practices are inspired by the excellent [pydavinci](https://github.com/pedrolabonia/pydavinci) library.

## Type Hints for DaVinci Resolve

### Why Use Type Hints?

Type hints provide several benefits:
- **IDE autocomplete** - Better development experience
- **Early error detection** - Catch bugs before runtime
- **Self-documenting code** - Clear function signatures
- **Refactoring safety** - Easier to maintain large codebases

### Basic Type Hints

```python
from typing import Dict, List, Optional, Literal

def apply_lut_to_clip(
    timeline_item,
    node_index: int,
    lut_filename: str
) -> bool:
    """
    Apply LUT to specific node.

    Args:
        timeline_item: TimelineItem object
        node_index: Node index (1-based)
        lut_filename: LUT filename in master directory

    Returns:
        True if successful, False otherwise
    """
    return timeline_item.SetLUT(node_index, lut_filename)
```

### Advanced Type Hints with Literal

```python
from typing import Literal

def add_color_version(
    timeline_item,
    version_name: str,
    version_type: Literal["local", "remote"] = "local"
) -> bool:
    """
    Add color version with type safety.

    Args:
        timeline_item: TimelineItem object
        version_name: Name for the version
        version_type: "local" (0) or "remote" (1)

    Returns:
        True if version was created successfully
    """
    version_type_int = 0 if version_type == "local" else 1
    return timeline_item.AddVersion(version_name, version_type_int)
```

### Type Hints for Complex Returns

```python
from typing import Dict, Any, Optional

def get_clip_properties(timeline_item) -> Dict[str, Any]:
    """
    Get clip properties as typed dictionary.

    Returns:
        Dictionary with clip metadata
    """
    return timeline_item.GetClipProperty()

def get_current_timeline(project) -> Optional[object]:
    """
    Get current timeline, may return None.

    Returns:
        Timeline object or None if no timeline is open
    """
    timeline = project.GetCurrentTimeline()
    return timeline if timeline else None
```

## Property Pattern

### Why Use Properties?

Properties provide a cleaner, more Pythonic interface:

```python
# ❌ Without properties (raw API)
timeline_name = timeline.GetName()
timeline.SetName("New Name")

# ✅ With properties (Pythonic)
timeline_name = timeline.name
timeline.name = "New Name"
```

### Implementing Properties

```python
class TimelineWrapper:
    """Wrapper for DaVinci Resolve Timeline with properties."""

    def __init__(self, timeline_obj):
        self._obj = timeline_obj

    @property
    def name(self) -> str:
        """Get timeline name."""
        return self._obj.GetName()

    @name.setter
    def name(self, value: str) -> None:
        """Set timeline name."""
        self._obj.SetName(value)

    @property
    def frame_rate(self) -> float:
        """Get timeline frame rate (read-only)."""
        setting = self._obj.GetSetting("timelineFrameRate")
        return float(setting) if setting else 0.0

    @property
    def start_frame(self) -> int:
        """Get timeline start frame."""
        return self._obj.GetStartFrame()
```

### Read-Only Properties

```python
@property
def unique_id(self) -> str:
    """Get unique ID (read-only)."""
    return self._obj.GetUniqueId()

# Attempting to set will raise AttributeError
# timeline.unique_id = "new_id"  # ❌ Error
```

## Error Handling Patterns

### Custom Exceptions

```python
class ResolveAPIError(Exception):
    """Base exception for DaVinci Resolve API errors."""
    pass

class ObjectNotFoundError(ResolveAPIError):
    """Raised when requested object is not found."""
    pass

class OperationFailedError(ResolveAPIError):
    """Raised when API operation fails."""
    pass
```

### Using Custom Exceptions

```python
def get_timeline_by_name(project, timeline_name: str):
    """
    Get timeline by name with proper error handling.

    Args:
        project: Project object
        timeline_name: Name of timeline to find

    Returns:
        Timeline object

    Raises:
        ObjectNotFoundError: If timeline not found
    """
    timeline_count = project.GetTimelineCount()

    for i in range(1, timeline_count + 1):
        timeline = project.GetTimelineByIndex(i)
        if timeline.GetName() == timeline_name:
            return timeline

    raise ObjectNotFoundError(f"Timeline '{timeline_name}' not found")

# Usage
try:
    timeline = get_timeline_by_name(project, "Main Edit")
except ObjectNotFoundError as e:
    print(f"❌ {e}")
    # Handle missing timeline
```

### Validation Functions

```python
def validate_node_index(timeline_item, node_index: int) -> bool:
    """
    Validate node index exists.

    Args:
        timeline_item: TimelineItem object
        node_index: Node index to validate (1-based)

    Returns:
        True if valid

    Raises:
        ValueError: If node_index is invalid
    """
    num_nodes = timeline_item.GetNumNodes()

    if num_nodes is None:
        raise OperationFailedError("Failed to get node count")

    if node_index < 1 or node_index > num_nodes:
        raise ValueError(
            f"Node index {node_index} out of range (1-{num_nodes})"
        )

    return True

# Usage
try:
    validate_node_index(timeline_item, 4)
    timeline_item.SetLUT(4, "my_lut.cube")
except ValueError as e:
    print(f"❌ Invalid node: {e}")
except OperationFailedError as e:
    print(f"❌ API error: {e}")
```

## Wrapper Pattern

### Basic Wrapper Implementation

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported during type checking, not at runtime
    from resolve_stubs import PyRemoteTimelineItem

class TimelineItemWrapper:
    """
    Pythonic wrapper for DaVinci Resolve TimelineItem.

    Provides type hints, properties, and cleaner interface.
    """

    def __init__(self, timeline_item_obj):
        """
        Initialize wrapper.

        Args:
            timeline_item_obj: Raw DaVinci Resolve TimelineItem object
        """
        self._obj = timeline_item_obj

    # Properties
    @property
    def name(self) -> str:
        return self._obj.GetName()

    @name.setter
    def name(self, value: str) -> None:
        self._obj.SetName(value)

    # LUT operations with type hints
    def set_lut(self, node_index: int, lut_path: str) -> bool:
        """
        Apply LUT to node.

        Args:
            node_index: Node index (1-based)
            lut_path: LUT filename

        Returns:
            True if successful
        """
        return self._obj.SetLUT(node_index, lut_path)

    def get_lut(self, node_index: int) -> str:
        """
        Get LUT from node.

        Args:
            node_index: Node index (1-based)

        Returns:
            LUT filename or empty string
        """
        return self._obj.GetLUT(node_index)

    # CDL operations
    def set_cdl(self, cdl_map: Dict[str, str]) -> bool:
        """
        Set CDL values.

        Args:
            cdl_map: Dictionary with keys:
                - NodeIndex: "1", "2", etc.
                - Slope: "R G B" e.g., "1.2 1.0 1.0"
                - Offset: "R G B" e.g., "0.0 0.0 0.0"
                - Power: "R G B" e.g., "1.0 1.0 1.0"
                - Saturation: "1.0"

        Returns:
            True if successful
        """
        return self._obj.SetCDL(cdl_map)

    # Color version management
    def add_color_version(
        self,
        version_name: str,
        version_type: Literal["local", "remote"] = "local"
    ) -> bool:
        """Add color version."""
        type_int = 0 if version_type == "local" else 1
        return self._obj.AddVersion(version_name, type_int)

    def load_color_version(
        self,
        version_name: str,
        version_type: Literal["local", "remote"] = "local"
    ) -> bool:
        """Load color version."""
        type_int = 0 if version_type == "local" else 1
        return self._obj.LoadVersionByName(version_name, type_int)

    def delete_color_version(
        self,
        version_name: str,
        version_type: Literal["local", "remote"] = "local"
    ) -> bool:
        """Delete color version."""
        type_int = 0 if version_type == "local" else 1
        return self._obj.DeleteVersionByName(version_name, type_int)

    def get_color_version_list(
        self,
        version_type: Literal["local", "remote"] = "local"
    ) -> List[str]:
        """Get list of color versions."""
        type_int = 0 if version_type == "local" else 1
        versions = self._obj.GetVersionNameList(type_int)
        return versions if versions else []
```

### Using the Wrapper

```python
# Wrap timeline item
timeline_item = timeline.GetItemListInTrack("video", 1)[0]
wrapped_item = TimelineItemWrapper(timeline_item)

# Pythonic property access
print(f"Clip name: {wrapped_item.name}")
wrapped_item.name = "Hero Shot"

# Type-safe LUT operations
success = wrapped_item.set_lut(4, "Classic_Cinema_Custom.cube")

# Type-safe version management
wrapped_item.add_color_version("Grade_v1", "local")
wrapped_item.load_color_version("Grade_v1", "local")
versions = wrapped_item.get_color_version_list("local")
```

## Render Job Monitoring Pattern

### Polling with Progress Display

```python
import time
from typing import Dict, List

def monitor_render_jobs(
    project,
    job_ids: List[str],
    poll_interval: float = 3.0
) -> None:
    """
    Monitor render jobs with progress display.

    Args:
        project: Project object
        job_ids: List of render job IDs
        poll_interval: Seconds between status checks
    """
    print(f"Monitoring {len(job_ids)} render job(s)...")

    completed_jobs = set()

    while len(completed_jobs) < len(job_ids):
        for job_id in job_ids:
            if job_id in completed_jobs:
                continue

            status = project.GetRenderJobStatus(job_id)

            if not status:
                print(f"⚠️  Job {job_id}: Status unavailable")
                continue

            job_status = status.get("JobStatus", "Unknown")
            complete_pct = status.get("CompletionPercentage", 0)

            if job_status == "Complete":
                completed_jobs.add(job_id)
                print(f"✅ Job {job_id}: Complete (100%)")
            elif job_status == "Failed":
                completed_jobs.add(job_id)
                error = status.get("Error", "Unknown error")
                print(f"❌ Job {job_id}: Failed - {error}")
            else:
                print(f"⏳ Job {job_id}: {job_status} ({complete_pct}%)")

        if len(completed_jobs) < len(job_ids):
            time.sleep(poll_interval)

    print("\n🎉 All render jobs completed")

# Usage
job_id = project.AddRenderJob()
if job_id:
    project.StartRendering(job_id)
    monitor_render_jobs(project, [job_id])
```

### Enhanced Progress with Time Estimation

```python
from datetime import datetime, timedelta

def monitor_render_with_eta(
    project,
    job_ids: List[str],
    poll_interval: float = 3.0
) -> None:
    """Monitor render jobs with ETA calculation."""
    print(f"Monitoring {len(job_ids)} render job(s)...")

    start_time = datetime.now()
    last_progress: Dict[str, float] = {job_id: 0.0 for job_id in job_ids}
    completed_jobs = set()

    while len(completed_jobs) < len(job_ids):
        for job_id in job_ids:
            if job_id in completed_jobs:
                continue

            status = project.GetRenderJobStatus(job_id)
            if not status:
                continue

            job_status = status.get("JobStatus", "Unknown")
            complete_pct = status.get("CompletionPercentage", 0)

            if job_status == "Complete":
                completed_jobs.add(job_id)
                print(f"✅ Job {job_id}: Complete")
                continue
            elif job_status == "Failed":
                completed_jobs.add(job_id)
                print(f"❌ Job {job_id}: Failed")
                continue

            # Calculate ETA
            elapsed = (datetime.now() - start_time).total_seconds()
            if complete_pct > 0 and complete_pct > last_progress[job_id]:
                total_time = elapsed / (complete_pct / 100.0)
                remaining = total_time - elapsed
                eta = timedelta(seconds=int(remaining))
                print(f"⏳ Job {job_id}: {complete_pct}% (ETA: {eta})")
            else:
                print(f"⏳ Job {job_id}: {complete_pct}%")

            last_progress[job_id] = complete_pct

        if len(completed_jobs) < len(job_ids):
            time.sleep(poll_interval)
```

## Best Practices Summary

### 1. Always Use Type Hints

```python
# ✅ Good
def apply_lut(item, node: int, lut: str) -> bool:
    return item.SetLUT(node, lut)

# ❌ Avoid
def apply_lut(item, node, lut):
    return item.SetLUT(node, lut)
```

### 2. Validate Inputs Early

```python
def set_lut_safe(timeline_item, node_index: int, lut_path: str) -> bool:
    # Validate node exists
    num_nodes = timeline_item.GetNumNodes()
    if not num_nodes or node_index > num_nodes:
        raise ValueError(f"Invalid node index: {node_index}")

    # Validate LUT exists (optional, depends on requirements)
    # ... validation logic ...

    # Apply LUT
    return timeline_item.SetLUT(node_index, lut_path)
```

### 3. Use Properties for Clean APIs

```python
# Create wrapper classes with properties for frequently-used objects
class ProjectWrapper:
    def __init__(self, project_obj):
        self._obj = project_obj

    @property
    def name(self) -> str:
        return self._obj.GetName()

    @property
    def current_timeline(self):
        return TimelineWrapper(self._obj.GetCurrentTimeline())
```

### 4. Handle None Returns

```python
# ✅ Good - Check for None
timeline = project.GetCurrentTimeline()
if timeline is None:
    print("❌ No timeline open")
    sys.exit(1)

# ❌ Avoid - Assuming non-None
items = timeline.GetItemListInTrack("video", 1)  # May crash if timeline is None
```

### 5. Use Literal for Restricted Values

```python
from typing import Literal

def set_clip_color(
    item,
    color: Literal["Orange", "Blue", "Green", "Red", "Yellow"]
) -> bool:
    """Set clip color with type-safe values."""
    return item.SetClipColor(color)
```

## Resources

### Recommended Libraries

- **[pydavinci](https://github.com/pedrolabonia/pydavinci)** - Type-safe DaVinci Resolve API wrapper
  - Full type hint coverage
  - Pythonic property interface
  - Enhanced error handling
  - Active development

### Installation

```bash
pip install pydavinci
```

### Usage with pydavinci

```python
from pydavinci import davinci

# Connect to Resolve
resolve = davinci.Resolve()

# Type-safe access with autocomplete
project = resolve.project
timeline = project.current_timeline

# Properties instead of Get/Set methods
print(f"Timeline: {timeline.name}")
timeline.name = "New Name"

# Enhanced color version management
item = timeline.video_track(1).clips[0]
item.add_color_version("Grade_v1", "local")
item.load_color_version("Grade_v1", "local")
```

## Migration from Raw API

### Before (Raw API)

```python
import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()
items = timeline.GetItemListInTrack("video", 1)
first_item = items[0]

# Apply LUT
first_item.SetLUT(4, "my_lut.cube")

# Add version
first_item.AddVersion("Test_v1", 0)
first_item.LoadVersionByName("Test_v1", 0)
```

### After (Type-Safe Wrapper)

```python
from pydavinci import davinci

resolve = davinci.Resolve()
timeline = resolve.project.current_timeline
first_item = timeline.video_track(1).clips[0]

# Apply LUT (type-safe)
first_item.set_lut(4, "my_lut.cube")

# Add version (type-safe with literal)
first_item.add_color_version("Test_v1", "local")
first_item.load_color_version("Test_v1", "local")
```

Benefits:
- IDE autocomplete
- Type checking catches errors early
- Cleaner, more readable code
- No need to remember magic numbers (0/1 for version types)
