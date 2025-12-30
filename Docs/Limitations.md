# DaVinci Resolve API Limitations & Workarounds

## Overview

The DaVinci Resolve Python API is powerful but has significant limitations, especially for color grading automation. This document catalogs known limitations and proven workarounds.

## Node Graph Limitations

### Cannot Add Nodes Programmatically

**Limitation**: No API methods to add serial or parallel nodes.

**Missing APIs**:
- `AddNode()` - Does not exist
- `AddSerial()` - Does not exist
- `AddParallel()` - Does not exist
- `DeleteNode()` - Does not exist

**Workaround**: Use DRX (DaVinci Resolve Grade Exchange) templates

1. Create desired node structure manually in Resolve UI
2. Export as DRX file (Gallery → Right-click still → Export)
3. Apply via Python:

```python
graph = timeline_item.GetNodeGraph()
success = graph.ApplyGradeFromDRX("/path/to/template.drx", 0)
```

**gradeMode Options**:
- `0` - No keyframes (recommended for templates)
- `1` - Source Timecode aligned
- `2` - Start Frames aligned

### Cannot Manipulate Node Connections

**Limitation**: No API to connect/disconnect nodes or change node tree structure.

**Workaround**: Pre-configure all node connections in DRX template.

## Color Grading Limitations

### Cannot Adjust Primary Wheels

**Limitation**: No API methods to adjust Lift/Gamma/Gain wheels.

**Missing APIs**:
- `SetLift()` - Does not exist
- `SetGamma()` - Does not exist
- `SetGain()` - Does not exist

**Workaround**: Use CDL (Color Decision List) for basic adjustments:

```python
timeline_item.SetCDL({
    "NodeIndex": "1",
    "Slope": "1.2 1.0 1.0",      # Similar to Gain (R channel boost)
    "Offset": "0.1 0.0 0.0",     # Similar to Lift (R channel lift)
    "Power": "1.0 1.0 1.0",      # Similar to Gamma
    "Saturation": "1.1"          # Overall saturation
})
```

**CDL Limitations**:
- Less intuitive than wheels
- Limited compared to full primary controls
- No separate control for shadows/midtones/highlights

### Cannot Edit Curves

**Limitation**: No API for custom curves or RGB curves.

**Missing APIs**:
- `SetCustomCurve()` - Does not exist
- `AddCurvePoint()` - Does not exist

**Workaround**:
1. Pre-configure curves in DRX template, or
2. Use LUTs to achieve curve-like transformations

### Cannot Create Power Windows

**Limitation**: No API to create or manipulate power windows (vignettes, shapes).

**Missing APIs**:
- `AddWindow()` - Does not exist
- `SetWindowPosition()` - Does not exist

**Workaround**: Include power windows in DRX template.

## Effects & Plugins

### Cannot Add Effects Programmatically

**Limitation**: No API to add OpenFX or ResolveFX plugins.

**Missing APIs**:
- `AddEffect()` - Does not exist
- `SetEffectParameter()` - Does not exist

**Workaround**: Include effects in DRX template with desired parameters.

### Cannot Adjust Effect Parameters

**Limitation**: Once applied (via DRX), cannot modify effect parameters via API.

**Workaround**: Create multiple DRX templates with different parameter presets.

## LUT Management

### Custom Subfolder Not Recognized

**Problem**: LUTs in `Custom/` subfolder are not accessible via API.

```python
# This fails even if file exists
timeline_item.SetLUT(1, "Custom/my_lut.cube")  # ❌
```

**Solution**: Place LUTs in master directory:

```python
import shutil

lut_master = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
shutil.copy2("my_lut.cube", lut_master)

# Refresh LUT list
project.RefreshLUTList()

# Apply using filename only (no path)
timeline_item.SetLUT(1, "my_lut.cube")  # ✅
```

### Must Refresh LUT List

**Problem**: Newly copied LUTs are not immediately available.

**Solution**: Always call `RefreshLUTList()` after copying LUTs:

```python
project.RefreshLUTList()  # Critical!
timeline_item.SetLUT(1, "new_lut.cube")
```

## Timeline & Clip Limitations

### Cannot Set In/Out Points Programmatically

**Limitation**: No API to set clip in/out points after adding to timeline.

**Workaround**: Perform edit in Resolve UI before running automation.

### Limited Clip Property Access

**Limitation**: Cannot access all clip properties (some are read-only or unavailable).

**Example**:
```python
# Can read
name = timeline_item.GetName()
duration = timeline_item.GetDuration()

# Cannot set many properties
timeline_item.SetName("New Name")  # May not work on all clip types
```

## Project & Timeline Management

### Startup Script Limitations

**Problem**: `GetCurrentProject()` returns `None` in `.scriptlib` startup scripts.

**Reason**: Project manager UI hasn't loaded yet.

**Workaround**:
1. Use startup script only for environment setup (copying LUTs, etc.)
2. Run project-specific automation after opening project manually
3. Or use Fusion page scripts that run after project load

### Cannot Automate Page Switching Reliably

**Problem**: `resolve.OpenPage("color")` may not work as expected in all contexts.

**Workaround**:
- Manual page switch before running script, or
- Add delays and verification:

```python
resolve.OpenPage("color")
import time
time.sleep(1)  # Allow UI to update
```

## Data Persistence

### Limited Data Types in SetData/GetData

**Problem**: `fusion:SetData()` and `fusion:GetData()` only support primitive types.

```lua
-- ✅ Works
fusion:SetData("last_lut", "Classic_Cinema.cube")
fusion:SetData("render_count", 42)

-- ❌ Doesn't work reliably
fusion:SetData("complex_object", some_table)  -- May not retrieve correctly
```

**Workaround**: Serialize complex data to JSON and store as string:

```python
import json

data = {"luts": ["lut1.cube", "lut2.cube"], "settings": {...}}
project.SetSetting("custom_data", json.dumps(data))

# Retrieve
data = json.loads(project.GetSetting("custom_data"))
```

## Color Version Management

### Version Names Must Be Unique

**Problem**: `AddVersion()` fails if version name already exists.

**Solution**: Check and delete existing versions:

```python
existing = timeline_item.GetVersionNameList(0)
if "Test_v1" in existing:
    timeline_item.DeleteVersionByName("Test_v1", 0)

timeline_item.AddVersion("Test_v1", 0)
```

## API Method Inconsistencies

### GetNumNodes() Location Varies

**Problem**: Node count method exists on both `TimelineItem` and `NodeGraph`, but behavior differs.

```python
# ✅ Recommended
num_nodes = timeline_item.GetNumNodes()

# ⚠️ May return None
num_nodes = graph.GetNumNodes()
```

**Solution**: Always use `TimelineItem.GetNumNodes()`.

### Node Indices Are 1-Based

**Important**: Unlike most programming, node indices start at 1, not 0.

```python
timeline_item.SetLUT(1, "lut.cube")  # ✅ First node
timeline_item.SetLUT(0, "lut.cube")  # ❌ Invalid
```

## Platform Differences

### Path Separators

**Problem**: Windows uses backslashes, macOS/Linux use forward slashes.

**Solution**: Use `os.path.join()` or `pathlib.Path`:

```python
import os

# ✅ Cross-platform
lut_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", ...)

# ❌ Platform-specific
lut_dir = "C:\\ProgramData\\Blackmagic Design\\..."
```

### Environment Variables

**macOS**:
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
```

**Windows**:
```cmd
set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
```

**Linux**:
```bash
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
```

## Summary: What You Can and Cannot Do

| Task | API Support | Workaround |
|------|-------------|------------|
| Add nodes | ❌ | DRX template |
| Delete nodes | ❌ | DRX template |
| Connect nodes | ❌ | DRX template |
| Apply LUT | ✅ | `SetLUT()` |
| Remove LUT | ✅ | `SetLUT(node, "")` |
| Set CDL | ✅ | `SetCDL()` |
| Adjust primary wheels | ❌ | CDL (limited) or DRX |
| Edit curves | ❌ | LUT or DRX |
| Add power windows | ❌ | DRX template |
| Add effects | ❌ | DRX template |
| Create timeline | ✅ | `CreateTimeline()` |
| Add clips | ✅ | `AppendToTimeline()` |
| Render | ✅ | `AddRenderJob()` |
| Color versions | ✅ | `AddVersion()`, etc. |
| Project settings | ✅ | `SetSetting()` |

## Best Practices

1. **Embrace DRX templates** - They're not a hack, they're the official workflow for complex grading
2. **Test on single clips first** - Verify operations before batch processing
3. **Always refresh LUT list** - After copying new LUTs to directory
4. **Use version management** - For A/B testing and client reviews
5. **Check return values** - Most API calls return `True/False` for success
6. **Handle None gracefully** - Some methods return `None` on failure
7. **Use absolute paths** - Avoid relative paths for cross-platform compatibility

## Resources

- [Official API README](file:///Library/Application%20Support/Blackmagic%20Design/DaVinci%20Resolve/Developer/Scripting/README.txt)
- [Unofficial API Docs](https://extremraym.com/cloud/resolve-scripting-doc/)
- [X-Raym's Scripts](https://github.com/X-Raym/DaVinci-Resolve-Scripts)
- [Blackmagic Forum](https://forum.blackmagicdesign.com/viewforum.php?f=21)
