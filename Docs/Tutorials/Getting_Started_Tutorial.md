# Getting Started Tutorial

This tutorial will guide you through setting up and using DaVinci Resolve automation scripts for the first time.

## Prerequisites

Before starting, ensure you have:

- ✅ **DaVinci Resolve Studio** installed (free version has limited API access)
- ✅ **Python 3.6 or later** installed
- ✅ Basic command-line knowledge
- ✅ A test project with some clips (for trying out scripts)

## Step 1: Installation

### Automated Setup (Recommended)

Clone the repository and run the setup script:

**macOS / Linux:**
```bash
# Clone repository
git clone https://github.com/nobphotographr/davinci-resolve-automation.git
cd davinci-resolve-automation

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

**Windows:**
```cmd
# Clone repository
git clone https://github.com/nobphotographr/davinci-resolve-automation.git
cd davinci-resolve-automation

# Run setup
setup.bat
```

The setup script will:
1. Detect your platform
2. Configure environment variables
3. Install sample LUTs
4. Test API connection

### Verify Installation

After setup completes, verify the installation:

```bash
# Check environment variables
echo $RESOLVE_SCRIPT_API  # macOS/Linux
echo %RESOLVE_SCRIPT_API% # Windows

# Should output the path to DaVinci Resolve scripting directory
```

If you see an error, see [Troubleshooting Guide](../Troubleshooting.md).

## Step 2: Prepare DaVinci Resolve

Before running scripts, prepare your DaVinci Resolve environment:

1. **Launch DaVinci Resolve**
2. **Open or create a test project**
   - Use an existing project, or
   - Create new project: File → New Project
3. **Add some test clips** (if using new project)
   - Import a few video files to Media Pool
   - Add them to a timeline

**Important:** Keep DaVinci Resolve running while executing scripts!

## Step 3: Your First Script

Let's start with a simple script: Timeline Analyzer

### 3.1 Open a Timeline

In DaVinci Resolve:
1. Open the Edit or Color page
2. Ensure a timeline is active (visible)

### 3.2 Run Timeline Analyzer

```bash
# Navigate to repository (if not already there)
cd davinci-resolve-automation

# Run timeline analyzer
python3 Scripts/Utilities/timeline_analyzer.py
```

You should see output like:
```
======================================================================
Timeline Analysis
======================================================================

Timeline: My_Timeline
Resolution: 1920x1080
Frame Rate: 24.0 fps
Start Timecode: 01:00:00:00
Duration: 00:02:15:12 (3252 frames)

----------------------------------------------------------------------
Tracks
----------------------------------------------------------------------
Video Tracks: 2
Audio Tracks: 1

----------------------------------------------------------------------
Clips
----------------------------------------------------------------------
Total Clips: 5

Clips per Track:
  V1: 3 clips
  V2: 2 clips
...
```

**Congratulations!** You've run your first automation script! 🎉

## Step 4: Try More Scripts

### 4.1 Install a LUT

Let's install one of the sample LUTs:

```bash
# View sample LUTs
ls Examples/LUT/

# Install a LUT
python3 Scripts/Utilities/lut_installer.py Examples/LUT/Classic_Cinema_Custom.cube
```

Output:
```
✅ Installed: Classic_Cinema_Custom.cube
✅ LUT list refreshed in DaVinci Resolve
```

Now check DaVinci Resolve:
1. Go to Color page
2. Select a clip
3. Right-click on a node → LUTs
4. You should see "Classic_Cinema_Custom.cube" in the list!

### 4.2 Analyze Media Pool

```bash
# Show media pool statistics
python3 Scripts/Utilities/media_pool_organizer.py --stats
```

This displays:
- Total clips and bins
- Clips by resolution
- Clips by codec
- Clips by frame rate

### 4.3 Create a Project Backup

```bash
# Backup current project
python3 Scripts/Utilities/project_backup.py --backup --note "My first backup"
```

Output:
```
✅ Backup created successfully
   Size: 245.3 KB
   Path: ~/DaVinci_Resolve_Backups/MyProject_20250130_143022_My_first_backup.drp
```

Your project is now safely backed up!

## Step 5: Practical Workflows

Now that you're comfortable with basic scripts, let's try practical workflows.

### Workflow 1: Batch Apply LUT to Timeline

**Scenario:** Apply a LUT to all clips in your timeline.

```bash
# Apply LUT to all clips in video track 1
python3 Scripts/ColorGrading/batch_grade_apply.py \
  --lut Classic_Cinema_Custom.cube \
  --node 4 \
  --track 1
```

**What happens:**
1. Script finds all clips in video track 1
2. Applies the LUT to node 4 of each clip
3. Shows progress for each clip

### Workflow 2: Organize Media Pool by Resolution

**Scenario:** Your media pool is messy, organize clips by resolution.

```bash
# First, see what you have
python3 Scripts/Utilities/media_pool_organizer.py --stats

# Organize by resolution
python3 Scripts/Utilities/media_pool_organizer.py --organize-by resolution
```

**Result:** Clips are automatically sorted into bins like:
- 📁 1920x1080
- 📁 3840x2160
- 📁 1280x720

### Workflow 3: Export Metadata to CSV

**Scenario:** Document your clips with metadata.

```bash
# Export metadata with clip properties
python3 Scripts/Utilities/metadata_manager.py \
  --export project_metadata.csv \
  --properties
```

Open `project_metadata.csv` in Excel or Google Sheets to see:
- Clip names
- Resolutions
- Codecs
- Frame rates
- Any metadata fields (Scene, Shot, Take, etc.)

### Workflow 4: Setup Automated Backups

**Scenario:** Backup project regularly, keep only last 5 versions.

```bash
# Create alias for easy backups (macOS/Linux)
alias backup-resolve='python3 ~/davinci-resolve-automation/Scripts/Utilities/project_backup.py --backup --keep 5'

# Now you can simply run:
backup-resolve
```

Every time you run this, it:
1. Creates a new backup
2. Automatically deletes old backups
3. Keeps only the 5 most recent

## Step 6: Advanced Usage

### Using DRX Templates

DRX templates let you apply complete node structures.

1. **Create a node structure in Resolve:**
   - Open Color page
   - Add nodes and configure them
   - Right-click node graph → "Copy Node Graph"

2. **Export as DRX:**
   - Right-click → Export → Save as `.drx` file
   - Save to `Templates/DRX/my_template.drx`

3. **Apply to clips:**
   ```bash
   python3 Scripts/ColorGrading/batch_grade_apply.py \
     --drx Templates/DRX/my_template.drx \
     --all
   ```

### Targeting Specific Clips

Use clip color for selective grading:

1. **Mark clips in Resolve:**
   - Select clips you want to grade
   - Right-click → Clip Color → Orange

2. **Apply grade to orange clips only:**
   ```bash
   python3 Scripts/ColorGrading/batch_grade_apply.py \
     --lut film.cube \
     --node 4 \
     --color Orange
   ```

### Combining Operations

Apply multiple operations at once:

```bash
# Apply DRX template + LUT in one command
python3 Scripts/ColorGrading/batch_grade_apply.py \
  --drx Templates/DRX/4_node_base.drx \
  --lut Classic_Cinema_Custom.cube \
  --node 4 \
  --track 1
```

## Common Tasks Reference

Quick reference for daily tasks:

| Task | Command |
|------|---------|
| Backup project | `python3 Scripts/Utilities/project_backup.py --backup` |
| List backups | `python3 Scripts/Utilities/project_backup.py --list` |
| Install LUT | `python3 Scripts/Utilities/lut_installer.py my_lut.cube` |
| Apply LUT to track | `python3 Scripts/ColorGrading/batch_grade_apply.py --lut my_lut.cube --node 4 --track 1` |
| Analyze timeline | `python3 Scripts/Utilities/timeline_analyzer.py` |
| Media pool stats | `python3 Scripts/Utilities/media_pool_organizer.py --stats` |
| Export metadata | `python3 Scripts/Utilities/metadata_manager.py --export metadata.csv` |
| Add render job | `python3 Scripts/Utilities/render_manager.py --add --preset prores422hq` |

## Tips for Success

### 1. Keep DaVinci Resolve Running
Scripts need DaVinci Resolve to be running. Always start Resolve before executing scripts.

### 2. Test on Small Projects First
Before running scripts on important projects:
- Create a test project
- Try the script
- Verify results
- Then use on real projects

### 3. Use Dry-Run Mode
Many scripts support `--dry-run`:
```bash
# See what would happen without actually doing it
python3 Scripts/Utilities/media_pool_organizer.py --organize-by resolution --dry-run
```

### 4. Backup Before Major Changes
Always backup before running batch operations:
```bash
python3 Scripts/Utilities/project_backup.py --backup --note "Before batch grading"
```

### 5. Start with Small Batches
Instead of processing all clips at once:
```bash
# Start with one track
python3 Scripts/ColorGrading/batch_grade_apply.py --lut film.cube --node 4 --track 1

# Then move to next track
python3 Scripts/ColorGrading/batch_grade_apply.py --lut film.cube --node 4 --track 2
```

### 6. Check Help for Each Script
Every script has built-in help:
```bash
python3 Scripts/Utilities/script_name.py --help
```

## Troubleshooting

If you encounter issues:

1. **Check [Troubleshooting Guide](../Troubleshooting.md)** - Most common issues are covered
2. **Verify DaVinci Resolve is running**
3. **Ensure project and timeline are open**
4. **Check environment variables are set**

## Next Steps

Now that you're comfortable with the basics:

1. **Explore More Scripts**
   - Try render queue management
   - Experiment with metadata management
   - Create custom DRX templates

2. **Read Documentation**
   - [API Reference](../API_Reference.md) - Understand what's possible
   - [Best Practices](../Best_Practices.md) - Learn proven patterns
   - [Advanced Techniques](../Advanced_Techniques.md) - Discover community tips

3. **Automate Your Workflow**
   - Create shell aliases for common tasks
   - Write simple scripts combining multiple operations
   - Share your discoveries with the community

4. **Contribute**
   - Found a useful pattern? Share it!
   - See [Contributing Guide](../CONTRIBUTING.md)

## Summary

In this tutorial, you learned:

✅ How to install and setup the automation scripts
✅ How to run your first script (Timeline Analyzer)
✅ How to install LUTs programmatically
✅ How to backup projects
✅ How to apply batch grading operations
✅ How to organize media pool
✅ How to use DRX templates
✅ Practical workflows for daily use

**You're now ready to automate your DaVinci Resolve workflow!** 🎬

---

**Questions or issues?**
- [Troubleshooting Guide](../Troubleshooting.md)
- [GitHub Issues](https://github.com/nobphotographr/davinci-resolve-automation/issues)
- [Blackmagic Forum](https://forum.blackmagicdesign.com/viewforum.php?f=21)

Happy automating! 🚀
