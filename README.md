# DaVinci Resolve Automation

> Python scripts and knowledge base for automating DaVinci Resolve color grading workflows

[![GitHub stars](https://img.shields.io/github/stars/nobphotographr/davinci-resolve-automation?style=social)](https://github.com/nobphotographr/davinci-resolve-automation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

This repository contains practical Python scripts and documentation for automating DaVinci Resolve workflows using the official Resolve Python API. The focus is on color grading automation, LUT management, and project setup.

## 🎯 Use Cases

- **LUT Testing & Comparison**: Automatically apply and compare multiple LUTs
- **Project Setup**: Automated project creation with predefined node structures
- **Batch Processing**: Apply grading templates to multiple clips
- **Color Version Management**: Programmatically manage color versions
- **Workflow Automation**: Streamline repetitive color grading tasks

## ✨ Key Features

### 🎨 Color Grading Automation (11 scripts)
- **Professional Look Presets**: 8 cinematic looks (Netflix, ARRI, Teal & Orange, Film Stock)
- **LUT Management**: Install, apply, compare, and export/import LUTs
- **CDL Interchange**: Industry-standard ASC CDL export/import for Baselight, Nuke, etc.
- **Batch Grading**: Apply DRX templates, LUTs, and CDL to multiple clips
- **Color Temperature**: 7 white balance presets from tungsten to blue hour
- **Exposure Matching**: Lift/gamma/gain adjustment across clips
- **Saturation Control**: 5 presets from flat to vivid
- **Contrast Management**: S-curve presets (flat, natural, cinematic, high)
- **Grade Copy/Paste**: Copy grades between clips with versioning
- **Color Versions**: Create and manage color versions for A/B testing
- **Flexible Targeting**: Target clips by track, color, or apply to all

### 📊 Timeline & Media Analysis (8 scripts)
- **Timeline Comparison**: Compare two timelines and identify differences
- **Shot List Generation**: Export to CSV/JSON/Markdown with timecodes
- **Timeline Statistics**: Analyze clip counts, duration, LUT usage, node structure
- **Node Structure Analysis**: Document and analyze color node structures
- **Media Pool Organization**: Auto-organize by resolution, codec, smart bin patterns
- **Marker Management**: Bulk add, export, import, and analyze markers
- **Timeline Import/Export**: Backup and restore timeline data
- **Batch Timeline Creation**: Create multiple timelines with automation

### 🗂️ Project Management & Delivery (4 scripts)
- **Deliverables Checklist**: Generate checklists for broadcast, web, cinema, archive
- **Automated Backups**: Timestamp-based project backups with retention policies
- **Metadata Management**: Bulk import/export metadata via CSV/JSON
- **Conform Assistant**: Timeline matching, missing media detection, rename detection
- **Shot List Generation**: Professional shot lists for production tracking
- **Project Cleanup**: Batch delete test projects
- **Automated Setup**: Create projects with predefined structures

### 🎬 Workflow Tools (12 scripts)
- **Audio Sync Helper**: Multi-camera sync with scene/shot grouping
- **Proxy Management**: Offline/online workflow with proxy status checking
- **Speed Ramp Manager**: 7 speed presets from quarter-speed to hyper-speed
- **Stabilization Manager**: 5 stabilization presets with workflow guidance
- **Text/Title Generation**: Templates for slates, lower thirds, watermarks
- **Batch Clip Renamer**: 5 rename modes (prefix, suffix, regex, sequential, metadata)
- **Clip Color Manager**: Analyze, manage, and bulk-modify clip colors
- **Render Manager**: 7 production-ready presets with progress monitoring
- **Project Backup**: Automated backup, restore, and retention management

### 📱 Interactive Workflows (1 script)
- **iPhone Blackmagic Camera Workflow**: Fully automated, step-by-step interactive workflow
  - Auto-detects media from external drives
  - Creates project with proper settings (resolution, fps)
  - Imports and organizes media into bins (by time/resolution)
  - Applies color space transformations (Blackmagic Log → Rec.709)
  - 6 professional color presets with automatic CDL grading:
    - Natural (YouTube/Vlog), Cinematic (Teal & Orange), Vivid (Instagram/SNS)
    - Moody (Drama/Art), Warm Sunset (Travel/Lifestyle), Cool Modern (Tech/Business)
  - Timeline creation modes: empty, chronological, or skip
  - Automatic color grading applied to all timeline clips
  - Preview before execution with confirmation
  - Comprehensive error handling and logging
  - Proxy generation setup with quality options
  - Perfect for beginners with detailed explanations at each step

## 📁 Repository Structure

```
davinci-resolve-automation/
├── Scripts/
│   ├── ColorGrading/          # Color grading automation scripts
│   ├── ProjectManagement/     # Project setup and management
│   ├── Utilities/             # Helper utilities
│   └── Workflows/             # Interactive workflow scripts
├── Templates/
│   └── DRX/                   # DaVinci Resolve Grade Exchange files
├── Docs/
│   ├── API_Reference.md       # API documentation and notes
│   ├── Best_Practices.md      # Best practices and patterns
│   └── Limitations.md         # Known limitations and workarounds
└── Examples/
    └── LUT/                   # Example LUT files
```

## 🚀 Getting Started

### Prerequisites

- **DaVinci Resolve Studio** (Free version has limited API access)
- **Python 3.6+**
- **macOS, Windows, or Linux**

### Quick Start

#### Automated Setup (Recommended)

**macOS / Linux:**
```bash
git clone https://github.com/nobphotographr/davinci-resolve-automation.git
cd davinci-resolve-automation
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
git clone https://github.com/nobphotographr/davinci-resolve-automation.git
cd davinci-resolve-automation
setup.bat
```

The setup script will:
- ✅ Detect your platform (macOS/Windows/Linux)
- ✅ Configure environment variables
- ✅ Install sample LUTs to DaVinci Resolve directory
- ✅ Verify Python installation
- ✅ Test API connection to DaVinci Resolve

#### Manual Setup

If you prefer manual setup:

**macOS:**
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
```

**Windows:**
```cmd
set RESOLVE_SCRIPT_API=C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
```

**Linux:**
```bash
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
```

Then run a sample script:
```bash
python3 Scripts/ColorGrading/lut_comparison.py
```

## 📚 Available Scripts

**Total: 35 Scripts** across Color Grading, Project Management, and Utilities

### 🎨 Color Grading (11 scripts)

| Script | Description |
|--------|-------------|
| `apply_drx_template.py` | Apply DRX node templates to clips |
| `batch_grade_apply.py` | Batch apply DRX/LUT/CDL to multiple clips with flexible targeting |
| `cdl_export_import.py` | Export/import ASC CDL (Color Decision List) for industry interchange |
| `color_temperature_adjuster.py` | Batch adjust white balance with 7 temperature presets |
| `contrast_manager.py` | Manage contrast with S-curve presets (flat, natural, cinematic, high) |
| `exposure_matcher.py` | Match exposure across clips using lift/gamma/gain |
| `grade_copy_paste.py` | Copy/paste color grades between clips with versioning |
| `lut_comparison.py` | Create color versions for easy LUT A/B comparison |
| `lut_comparison_generator.py` | Generate side-by-side LUT comparison timeline |
| `quick_look_presets.py` | Apply professional looks (Netflix, ARRI, Teal & Orange, Film Stock) |
| `saturation_controller.py` | Batch saturation control with 5 presets (flat to vivid) |

### 🗂️ Project Management (4 scripts)

| Script | Description |
|--------|-------------|
| `auto_project_setup.py` | Create projects with automated settings |
| `cleanup_projects.py` | Remove test projects in bulk |
| `deliverables_checklist.py` | Generate delivery checklists (broadcast, web, cinema, archive) |
| `shot_list_generator.py` | Generate shot lists in CSV/JSON/Markdown with timecodes |

### 🛠️ Utilities (20 scripts)

| Script | Description |
|--------|-------------|
| `audio_sync_helper.py` | Multi-camera sync assistance with scene/shot grouping |
| `batch_clip_renamer.py` | Rename clips with 5 modes (prefix, suffix, regex, sequential, metadata) |
| `batch_speed_ramp.py` | Manage speed ramps with 7 presets (quarter-speed to hyper-speed) |
| `batch_stabilization_manager.py` | Stabilization management with 5 presets (light to strong) |
| `batch_text_title_generator.py` | Text/title generation assistant (slates, lower thirds, watermarks) |
| `batch_timeline_creator.py` | Create multiple timelines with automated settings |
| `clip_color_manager.py` | Manage, analyze, and bulk-modify clip colors |
| `conform_assistant.py` | Timeline comparison, missing media detection, conform verification |
| `lut_installer.py` | Install custom LUTs to Resolve directory with auto-refresh |
| `marker_manager.py` | Bulk marker management (add, export, import, analyze) |
| `media_pool_organizer.py` | Organize media pool by resolution/codec, search, cleanup |
| `metadata_manager.py` | Bulk manage, import/export metadata (CSV/JSON) |
| `node_structure_analyzer.py` | Analyze and document node structures across clips |
| `project_backup.py` | Automated project backup, restore, and retention management |
| `proxy_workflow_manager.py` | Proxy workflow management for offline/online editing |
| `render_manager.py` | Render queue management with 7 built-in presets |
| `smart_bin_organizer.py` | Intelligent bin organization with pattern matching |
| `timeline_analyzer.py` | Analyze timeline statistics, LUT usage, clip distribution |
| `timeline_comparison.py` | Compare two timelines and identify differences |
| `timeline_export_import.py` | Export/import timeline data with clip information |

### 📱 Workflows (1 script)

| Script | Description |
|--------|-------------|
| `iphone_bmc_interactive.py` | Interactive iPhone Blackmagic Camera workflow with full automation |

**iPhone BMC Workflow Features:**
- 7-step interactive guide with detailed explanations
- Auto-detects media from external drives
- Creates project with proper settings (resolution, fps)
- Imports and organizes media into bins (by time/resolution)
- Applies color space transformations (Blackmagic Log → Rec.709)
- 6 professional color presets with automatic CDL application:
  - Natural (YouTube/Vlog), Cinematic (Teal & Orange), Vivid (Instagram/SNS)
  - Moody (Drama/Art), Warm Sunset (Travel/Lifestyle), Cool Modern (Tech/Business)
- Timeline creation modes: empty, chronological, or skip
- Automatic color grading applied to all timeline clips (CDL: Slope, Offset, Power, Saturation)
- Preview before execution with user confirmation
- Comprehensive error handling with detailed logging
- Proxy generation setup with quality options

## 🎬 Detailed Usage Examples

### LUT Installation & Management

**Install LUTs:**
```bash
# Install single LUT
python3 Scripts/Utilities/lut_installer.py my_lut.cube

# Install multiple LUTs
python3 Scripts/Utilities/lut_installer.py lut1.cube lut2.cube lut3.cube

# Install with overwrite
python3 Scripts/Utilities/lut_installer.py --overwrite my_lut.cube
```

### Timeline Analysis

**Analyze your timeline:**
```bash
# Basic statistics
python3 Scripts/Utilities/timeline_analyzer.py

# Detailed per-clip info
python3 Scripts/Utilities/timeline_analyzer.py --detailed

# Export to JSON
python3 Scripts/Utilities/timeline_analyzer.py --json timeline_report.json
```

### Batch Grading

**Apply grades to multiple clips:**
```bash
# Apply DRX to all clips in track 1
python3 Scripts/ColorGrading/batch_grade_apply.py --drx template.drx --track 1

# Apply LUT to all clips
python3 Scripts/ColorGrading/batch_grade_apply.py --lut my_lut.cube --node 4 --all

# Apply to orange-colored clips only
python3 Scripts/ColorGrading/batch_grade_apply.py --lut film.cube --node 4 --color Orange

# Combine DRX and LUT
python3 Scripts/ColorGrading/batch_grade_apply.py --drx base.drx --lut film.cube --node 4 --all
```

### Render Queue Management

**Manage rendering:**
```bash
# List available presets
python3 Scripts/Utilities/render_manager.py --list-presets

# Add render job with ProRes preset
python3 Scripts/Utilities/render_manager.py --add --preset prores422hq --output ~/renders/

# Start rendering with progress monitoring
python3 Scripts/Utilities/render_manager.py --start --monitor

# View queue status
python3 Scripts/Utilities/render_manager.py --status
```

### Media Pool Organization

**Organize your media:**
```bash
# Show statistics
python3 Scripts/Utilities/media_pool_organizer.py --stats

# Display bin structure as tree
python3 Scripts/Utilities/media_pool_organizer.py --tree

# Auto-organize by resolution
python3 Scripts/Utilities/media_pool_organizer.py --organize-by resolution

# Auto-organize by codec
python3 Scripts/Utilities/media_pool_organizer.py --organize-by codec

# Search for clips
python3 Scripts/Utilities/media_pool_organizer.py --search "interview"

# Clean empty bins (dry-run first)
python3 Scripts/Utilities/media_pool_organizer.py --clean-empty-bins --dry-run
python3 Scripts/Utilities/media_pool_organizer.py --clean-empty-bins
```

### Metadata Management

**Manage clip metadata:**
```bash
# List all metadata
python3 Scripts/Utilities/metadata_manager.py --list

# Export to CSV with properties
python3 Scripts/Utilities/metadata_manager.py --export metadata.csv --properties

# Import from CSV
python3 Scripts/Utilities/metadata_manager.py --import metadata.csv

# Set metadata on specific clips
python3 Scripts/Utilities/metadata_manager.py --set-field "Scene" "101A" --search "interview"

# Find clips by metadata
python3 Scripts/Utilities/metadata_manager.py --find-by "Scene=101"

# Work with timeline clips
python3 Scripts/Utilities/metadata_manager.py --timeline --list
```

### Project Backup

**Backup and restore:**
```bash
# Create backup
python3 Scripts/Utilities/project_backup.py --backup

# Backup with note
python3 Scripts/Utilities/project_backup.py --backup --note "Before major changes"

# Backup with retention (keep last 5)
python3 Scripts/Utilities/project_backup.py --backup --keep 5

# List all backups
python3 Scripts/Utilities/project_backup.py --list

# Clean old backups
python3 Scripts/Utilities/project_backup.py --clean --keep 10 --dry-run

# Restore from backup
python3 Scripts/Utilities/project_backup.py --restore MyProject_20250130_143022.drp
```

### Clip Color Management

**Manage clip colors:**
```bash
# Show color distribution statistics
python3 Scripts/Utilities/clip_color_manager.py --stats

# List clips with specific color
python3 Scripts/Utilities/clip_color_manager.py --list --color Orange

# Set color on clips matching search
python3 Scripts/Utilities/clip_color_manager.py --set-color Blue --search "interview"

# Clear color from specific clips
python3 Scripts/Utilities/clip_color_manager.py --clear-color --color Orange

# Clear all colors (dry-run first)
python3 Scripts/Utilities/clip_color_manager.py --clear-color --dry-run

# Work with timeline clips
python3 Scripts/Utilities/clip_color_manager.py --timeline --stats
python3 Scripts/Utilities/clip_color_manager.py --timeline --set-color Purple --search "b-roll"
```

### Color Grading Workflows

**Apply professional cinematic looks:**
```bash
# List available looks
python3 Scripts/ColorGrading/quick_look_presets.py --list-looks

# Apply Netflix look to all clips
python3 Scripts/ColorGrading/quick_look_presets.py --look netflix --all

# Apply Teal & Orange to specific track
python3 Scripts/ColorGrading/quick_look_presets.py --look teal-orange --track 1
```

**Adjust color temperature:**
```bash
# List temperature presets
python3 Scripts/ColorGrading/color_temperature_adjuster.py --list-presets

# Apply daylight preset to all clips
python3 Scripts/ColorGrading/color_temperature_adjuster.py --preset daylight --all

# Set custom temperature
python3 Scripts/ColorGrading/color_temperature_adjuster.py --temperature 5600 --tint 0 --all
```

**Manage saturation:**
```bash
# Apply cinematic saturation preset
python3 Scripts/ColorGrading/saturation_controller.py --preset cinematic --all

# Set custom saturation value
python3 Scripts/ColorGrading/saturation_controller.py --saturation 1.2 --track 1

# Reset to neutral
python3 Scripts/ColorGrading/saturation_controller.py --reset --all
```

**Export/Import CDL:**
```bash
# Export CDL from all clips
python3 Scripts/ColorGrading/cdl_export_import.py --export grades.cdl --all

# Import CDL to clips
python3 Scripts/ColorGrading/cdl_export_import.py --import grades.cdl --all

# Show CDL info
python3 Scripts/ColorGrading/cdl_export_import.py --info --all
```

### Timeline & Workflow Tools

**Generate shot lists:**
```bash
# Generate CSV shot list
python3 "Scripts/Project Management/shot_list_generator.py" --output shots.csv --format csv

# Generate detailed Markdown report
python3 "Scripts/Project Management/shot_list_generator.py" --output report.md --format markdown --detailed

# Summary only
python3 "Scripts/Project Management/shot_list_generator.py" --summary
```

**Compare timelines:**
```bash
# Compare two timelines
python3 Scripts/Utilities/conform_assistant.py --compare --timeline1 "Edit_v1" --timeline2 "Edit_v2"

# Find missing media
python3 Scripts/Utilities/conform_assistant.py --find-missing --output missing.txt

# Generate conform report
python3 Scripts/Utilities/conform_assistant.py --report conform.md
```

**Manage markers:**
```bash
# Add markers to all clips
python3 Scripts/Utilities/marker_manager.py --add "Review Point" --all

# Export markers to CSV
python3 Scripts/Utilities/marker_manager.py --export markers.csv

# Show marker statistics
python3 Scripts/Utilities/marker_manager.py --stats
```

### Delivery & Quality Control

**Generate deliverables checklist:**
```bash
# List available templates
python3 "Scripts/Project Management/deliverables_checklist.py" --list-templates

# Generate broadcast delivery checklist
python3 "Scripts/Project Management/deliverables_checklist.py" --template broadcast --output checklist.md

# Quick project status check
python3 "Scripts/Project Management/deliverables_checklist.py" --quick-check
```

**Proxy workflow management:**
```bash
# Show proxy workflow guide
python3 Scripts/Utilities/proxy_workflow_manager.py --workflow-guide

# Check proxy status
python3 Scripts/Utilities/proxy_workflow_manager.py --status --all

# Check for missing proxies
python3 Scripts/Utilities/proxy_workflow_manager.py --check-missing --all

# Generate proxy report
python3 Scripts/Utilities/proxy_workflow_manager.py --report proxies.csv
```

### iPhone Blackmagic Camera Workflow

**Interactive iPhone BMC workflow:**
```bash
# Run the interactive workflow assistant
python3 Scripts/Workflows/iphone_bmc_interactive.py
```

**What the workflow does:**
1. **Auto-detects media** from external drives (DCIM, PRIVATE, Blackmagic folders)
2. **Creates project** with your chosen resolution (1080p/4K/portrait) and fps (24/30/60)
3. **Imports media** and organizes into bins by:
   - Time of day (Morning/Afternoon/Evening)
   - Resolution (4K/1080p/Other)
   - All in root folder
4. **Applies color space transformation** and **automatic color grading**:
   - Color space: Blackmagic Log → Rec.709
   - 6 professional color presets with automatic CDL application:
     - Natural: Clean, neutral look for YouTube/Vlogs
     - Cinematic: Teal & Orange Hollywood look with dramatic contrast
     - Vivid: High saturation and punchy colors for Instagram/SNS
     - Moody: Low contrast, faded colors for Drama/Art
     - Warm Sunset: Golden hour look for Travel/Lifestyle
     - Cool Modern: Blue tones for Tech/Business
   - Custom: Use your own LUT file
   - CDL values (Slope, Offset, Power, Saturation) applied to all clips
5. **Preview & Confirmation**:
   - Shows complete preview of all settings before execution
   - User confirmation required to proceed
   - Detailed logging to file for troubleshooting
6. **Creates timeline**:
   - Empty timeline for manual editing
   - Chronological timeline with all clips sorted
   - Skip to create timeline later
7. **Sets up proxies** with half or quarter resolution options

**Perfect for:**
- iPhone Blackmagic Camera users (ProRes, Log recording)
- Beginners who want guided workflow with automatic color grading
- Quick project setup with professional color management
- Vertical video creators (Instagram, TikTok, YouTube Shorts)
- Content creators who need consistent looks across projects

## 💡 Key Concepts

### DRX Templates

DaVinci Resolve Grade Exchange (DRX) files store complete node structures. Since the Python API doesn't support adding nodes programmatically, we use DRX templates as a workaround:

1. Create node structure manually in Resolve UI
2. Export as DRX file
3. Apply via Python API: `graph.ApplyGradeFromDRX(path, 0)`

### Color Version Management

Newly discovered API feature for managing color variations:

```python
# Create versions for different LUTs
timeline_item.AddVersion("Classic_Cinema", 0)
timeline_item.LoadVersionByName("Classic_Cinema", 0)
timeline_item.SetLUT(4, "Classic_Cinema.cube")
```

Switch between versions in Resolve UI for instant comparison!

## 📖 Documentation

### Tutorials
- **[Getting Started Tutorial](Docs/Tutorials/Getting_Started_Tutorial.md)** - Complete beginner's guide 🚀

### Reference
- **[Troubleshooting](Docs/Troubleshooting.md)** - Common issues and solutions 🔧
- **[API Reference](Docs/API_Reference.md)** - Complete API documentation
- **[Best Practices](Docs/Best_Practices.md)** - Proven patterns and strategies
- **[Limitations](Docs/Limitations.md)** - Known API limitations and workarounds
- **[Advanced Techniques](Docs/Advanced_Techniques.md)** - Community-discovered workarounds and techniques
- **[Type Safety & Best Practices](Docs/Type_Safety_and_Best_Practices.md)** - Modern Python patterns with type hints

### Contributing
- **[Contributing](Docs/CONTRIBUTING.md)** - How to add knowledge to this repository

## 🔧 API Capabilities & Limitations

### ✅ What You Can Do

- Apply LUTs to existing nodes
- Set CDL values (Slope, Offset, Power, Saturation)
- Apply DRX templates (complete node structures)
- Manage color versions
- Create/manage projects and timelines
- Add/remove clips
- Configure render jobs

### ❌ What You Can't Do (Workarounds Available)

- **Add nodes dynamically** → Use DRX templates
- **Adjust curves** → Pre-configure in DRX or use CDL
- **Add effects/plugins** → Include in DRX template
- **Create power windows** → Pre-configure in DRX

See [Limitations.md](Docs/Limitations.md) for detailed workarounds.

## 🌟 Example Workflow

### Automated LUT Testing

```python
from Scripts.ColorGrading.lut_comparison import create_lut_versions

# Create color versions for each LUT
luts = [
    "Classic_Cinema.cube",
    "Teal_Orange.cube",
    "Film_Emulation.cube"
]

create_lut_versions(luts)
# Now switch between versions in Resolve UI!
```

### Batch Project Setup

```python
from Scripts.ProjectManagement.auto_project_setup import setup_project

# Create project with 4-node structure + LUT
setup_project(
    project_name="MyProject",
    media_path="/path/to/footage.braw",
    drx_template="Templates/DRX/4_node_cinematic.drx",
    lut="Classic_Cinema.cube"
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📝 Resources

### Official Documentation

- [DaVinci Resolve Scripting README](file:///Library/Application%20Support/Blackmagic%20Design/DaVinci%20Resolve/Developer/Scripting/README.txt)
- [Blackmagic Forum - Scripting](https://forum.blackmagicdesign.com/viewforum.php?f=21)

### Recommended Libraries

- **[pydavinci](https://github.com/pedrolabonia/pydavinci)** - Type-safe Python API wrapper
  - Full type hint coverage for IDE autocomplete
  - Pythonic property interface
  - Enhanced error handling
  - Modern Python patterns
  - `pip install pydavinci`

### Community Resources

- [extremraym - Unofficial API Docs](https://extremraym.com/cloud/resolve-scripting-doc/)
- [X-Raym/DaVinci-Resolve-Scripts](https://github.com/X-Raym/DaVinci-Resolve-Scripts) - Lua script collection
- [hitsugi_yukana - Fusion Page Scripting](https://zenn.dev/hitsugi_yukana) - Japanese articles on Fusion scripting
- [DaVinci Resolve 起動時スクリプト自動実行](https://zenn.dev/hitsugi_yukana/articles/536b36e1c97315) - Japanese startup script guide

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 👤 Author

**Nobu** - [@nobphotographr](https://github.com/nobphotographr)

## 🙏 Acknowledgments

- Blackmagic Design for DaVinci Resolve and the Python API
- X-Raym for pioneering Resolve scripting examples
- The DaVinci Resolve scripting community

---

**Note**: This is an independent project and is not affiliated with Blackmagic Design.
