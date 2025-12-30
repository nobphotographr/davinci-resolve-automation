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

## 📁 Repository Structure

```
davinci-resolve-automation/
├── Scripts/
│   ├── ColorGrading/          # Color grading automation scripts
│   ├── ProjectManagement/     # Project setup and management
│   └── Utilities/             # Helper utilities
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

### Color Grading

| Script | Description |
|--------|-------------|
| `lut_comparison.py` | Create color versions for easy LUT A/B comparison |
| `apply_drx_template.py` | Apply DRX node templates to clips |
| `batch_grade_apply.py` | Batch apply DRX/LUT/CDL to multiple clips with flexible targeting |

### Project Management

| Script | Description |
|--------|-------------|
| `auto_project_setup.py` | Create projects with automated settings |
| `cleanup_test_projects.py` | Remove test projects in bulk |

### Utilities

| Script | Description |
|--------|-------------|
| `lut_installer.py` | Install custom LUTs to Resolve directory with auto-refresh |
| `timeline_analyzer.py` | Analyze timeline statistics, LUT usage, and clip distribution |
| `render_manager.py` | Manage render queue, add jobs with presets, monitor progress |

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

- **[API Reference](Docs/API_Reference.md)** - Complete API documentation
- **[Best Practices](Docs/Best_Practices.md)** - Proven patterns and strategies
- **[Limitations](Docs/Limitations.md)** - Known API limitations and workarounds
- **[Advanced Techniques](Docs/Advanced_Techniques.md)** - Community-discovered workarounds and techniques
- **[Type Safety & Best Practices](Docs/Type_Safety_and_Best_Practices.md)** - Modern Python patterns with type hints
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
