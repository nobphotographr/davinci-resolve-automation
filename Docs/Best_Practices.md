# Best Practices for DaVinci Resolve Automation

## DRX Template Strategy

### When to Use DRX Templates

Use DRX templates for any node structure that can't be created via API:

- Multiple serial nodes
- Parallel node configurations
- Nodes with effects/plugins
- Complex grading setups

### Creating Effective DRX Templates

1. **Keep it modular**: Create templates for specific purposes
2. **Use descriptive names**: `4_node_cinematic.drx`, `teal_orange_advanced.drx`
3. **Document node roles**: Add node labels in Resolve before exporting
4. **Test on clean clips**: Ensure templates work on neutral footage

### Example Template Workflow

```python
# 1. Create node structure manually in Resolve UI
# 2. Export as DRX
# 3. Apply via Python

drx_path = "Templates/DRX/4_node_cinematic.drx"
graph = timeline_item.GetNodeGraph()
graph.ApplyGradeFromDRX(drx_path, 0)  # gradeMode=0: No keyframes
```

## LUT Management

### LUT Path Handling

**Problem**: `Custom` subfolder not recognized by API

**Solution**: Place LUTs in master directory

```python
import shutil

# Copy to master LUT directory
lut_master = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
shutil.copy2("my_lut.cube", lut_master)

# Refresh and apply (filename only)
project.RefreshLUTList()
timeline_item.SetLUT(1, "my_lut.cube")
```

### LUT Testing Workflow

Use color versions for efficient A/B testing:

```python
luts_to_test = [
    ("Classic_Cinema", "classic_cinema.cube"),
    ("Teal_Orange", "teal_orange.cube"),
    ("No_LUT", "")
]

for version_name, lut_path in luts_to_test:
    timeline_item.AddVersion(version_name, 0)
    timeline_item.LoadVersionByName(version_name, 0)
    if lut_path:
        timeline_item.SetLUT(4, lut_path)
```

## Color Version Management

### Best Practices

1. **Use descriptive names**: "Grade_v1_Warm", "Grade_v2_Cool"
2. **Version type 0 for local**: Use local versions (type=0) for testing
3. **Clean up old versions**: Delete test versions when done

```python
# Check existing versions before creating
versions = timeline_item.GetVersionNameList(0)
if "Test_v1" in versions:
    timeline_item.DeleteVersionByName("Test_v1", 0)
```

## Project Setup Automation

### Naming Conventions

Use timestamps for unique project names:

```python
import time
timestamp = int(time.time())
project_name = f"LUT_Test_{timestamp}"
```

### Color Management Settings

```python
# Set color science
project.SetSetting("colorScienceMode", "davinciYRGBColorManaged")

# Set timeline color space
project.SetSetting("timelineColorSpaceTag", "Rec.709-A")
```

### Error Handling

Always verify API calls:

```python
project = project_manager.CreateProject(project_name)
if not project:
    print(f"❌ Failed to create project: {project_name}")
    sys.exit(1)
```

## Performance Optimization

### Batch Operations

Process multiple clips in a single script run:

```python
timeline_items = timeline.GetItemListInTrack("video", 1)

for item in timeline_items:
    # Apply same DRX to all clips
    graph = item.GetNodeGraph()
    graph.ApplyGradeFromDRX(drx_path, 0)
```

### Minimize Resolve Page Switches

```python
# Open Color page once at start
resolve.OpenPage("color")

# Process all clips
# ...

# Only switch pages when necessary
```

## CDL Usage

### When to Use CDL

- Basic color adjustments (contrast, brightness)
- Parametric adjustments needed after DRX application
- Automating simple grading tasks

### CDL Example

```python
timeline_item.SetCDL({
    "NodeIndex": "1",
    "Slope": "1.2 1.2 1.2",     # Increase contrast
    "Offset": "0.0 0.0 0.0",    # No offset
    "Power": "1.0 1.0 1.0",     # No power change
    "Saturation": "1.1"         # Slight saturation boost
})
```

## Testing & Debugging

### Start with Small Tests

```python
# Test on single clip first
first_item = timeline_items[0]
success = first_item.SetLUT(1, "test.cube")
print(f"LUT application: {'✅' if success else '❌'}")
```

### Verify Node Count

```python
num_nodes = timeline_item.GetNumNodes()
if num_nodes:
    print(f"Nodes available: {num_nodes}")
    for i in range(1, num_nodes + 1):
        label = timeline_item.GetNodeLabel(i)
        print(f"  Node {i}: {label}")
```

### Check Current State

```python
# Check current LUT
current_lut = timeline_item.GetLUT(1)
print(f"Current LUT on node 1: {current_lut}")

# Check current version
current_version = timeline_item.GetCurrentVersion()
print(f"Current version: {current_version}")
```

## Common Pitfalls

### 1. Forgetting to Refresh LUT List

```python
# ❌ Wrong
timeline_item.SetLUT(1, "new_lut.cube")  # Fails if Resolve hasn't discovered it

# ✅ Correct
project.RefreshLUTList()
timeline_item.SetLUT(1, "new_lut.cube")
```

### 2. Node Index Off-by-One

```python
# Node indices are 1-based, not 0-based
timeline_item.SetLUT(1, "lut.cube")  # ✅ First node
timeline_item.SetLUT(0, "lut.cube")  # ❌ Invalid
```

### 3. Hardcoded Paths

```python
# ❌ Platform-specific
lut_dir = "C:\\ProgramData\\Blackmagic Design\\..."

# ✅ Cross-platform
import os
lut_dir = os.path.expanduser("~/Library/Application Support/...")
```

## Lua vs Python

### When to Use Lua

- Startup scripts (`.scriptlib`)
- Fusion page operations
- UI scripting

### When to Use Python

- Complex logic
- External library integration
- Data processing
- File operations

### Calling Python from Lua

```lua
fusion:RunScript("!Py3: /path/to/script.py")
```

## Documentation

Always document your scripts:

```python
"""
Script Name: batch_lut_apply.py
Purpose: Apply LUT to all clips in timeline
Usage: python3 batch_lut_apply.py <lut_name>
Author: Your Name
Date: 2025-01-01
"""
```

## Version Control

Track your DRX templates and scripts:

```bash
git init
git add Scripts/ Templates/ Docs/
git commit -m "Initial commit"
```

## Resources

- Keep API documentation handy
- Test on duplicated projects
- Share successful patterns with community
