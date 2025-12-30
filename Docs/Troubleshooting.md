# Troubleshooting Guide

This guide covers common issues and their solutions when using DaVinci Resolve automation scripts.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Environment Setup Issues](#environment-setup-issues)
- [Script Execution Errors](#script-execution-errors)
- [API-Specific Issues](#api-specific-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Performance Issues](#performance-issues)

---

## Connection Issues

### "Could not connect to DaVinci Resolve"

**Problem:** Script cannot connect to DaVinci Resolve API.

**Solutions:**

1. **Ensure DaVinci Resolve is running**
   ```bash
   # The application must be running before executing scripts
   ```

2. **Verify you have DaVinci Resolve Studio**
   - Free version has limited API access
   - Some scripts require Studio version

3. **Check environment variables**
   ```bash
   # macOS/Linux
   echo $RESOLVE_SCRIPT_API
   echo $RESOLVE_SCRIPT_LIB

   # Windows
   echo %RESOLVE_SCRIPT_API%
   echo %RESOLVE_SCRIPT_LIB%
   ```

4. **Restart DaVinci Resolve**
   - Sometimes the API connection needs a fresh start
   - Close and reopen DaVinci Resolve

5. **Verify API files exist**
   ```bash
   # macOS
   ls "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"

   # Windows
   dir "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"

   # Linux
   ls /opt/resolve/Developer/Scripting
   ```

---

## Environment Setup Issues

### "DaVinci Resolve Python API not available"

**Problem:** Python cannot import DaVinciResolveScript module.

**Solutions:**

1. **Re-run setup script**
   ```bash
   # macOS/Linux
   ./setup.sh

   # Windows
   setup.bat
   ```

2. **Manually set environment variables**

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

3. **Add to shell configuration permanently**

   **macOS (zsh):**
   ```bash
   echo 'export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"' >> ~/.zshrc
   echo 'export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"' >> ~/.zshrc
   source ~/.zshrc
   ```

   **Linux (bash):**
   ```bash
   echo 'export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"' >> ~/.bashrc
   echo 'export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Python Version Issues

**Problem:** Script fails with syntax errors or import errors.

**Solution:**

Ensure Python 3.6 or later is installed:
```bash
python3 --version
```

If version is too old, install a newer Python version from [python.org](https://www.python.org/).

---

## Script Execution Errors

### "No project is currently open"

**Problem:** Script requires an open project but none is loaded.

**Solution:**
1. Open DaVinci Resolve
2. Open or create a project
3. Run the script again

### "No timeline is currently open"

**Problem:** Script requires an active timeline.

**Solution:**
1. Open a timeline in DaVinci Resolve
2. Ensure the timeline is visible in the Color or Edit page
3. Run the script again

### "No clips found matching criteria"

**Problem:** Script cannot find clips with specified criteria.

**Solution:**

1. **Verify clips exist:**
   - Check that clips are in the media pool or timeline
   - Use `--all` flag to target all clips first

2. **Check search parameters:**
   ```bash
   # If searching by name
   python3 metadata_manager.py --search "interview"

   # Try broader search
   python3 metadata_manager.py --search "inter"
   ```

3. **Check clip color:**
   ```bash
   # Verify clip colors in Resolve UI
   # Colors are case-sensitive: "Orange" not "orange"
   python3 batch_grade_apply.py --lut film.cube --node 4 --color "Orange"
   ```

### Permission Denied Errors

**Problem:** Cannot write to LUT directory or backup location.

**Solution:**

1. **LUT installation permission issues (macOS/Linux):**
   ```bash
   # Check directory permissions
   ls -la "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"

   # May need sudo for system directories
   sudo python3 Scripts/Utilities/lut_installer.py my_lut.cube
   ```

2. **Use custom output directory:**
   ```bash
   # For LUT installer
   python3 Scripts/Utilities/lut_installer.py --dest ~/MyLUTs my_lut.cube

   # For project backup
   python3 Scripts/Utilities/project_backup.py --backup --output ~/MyBackups
   ```

---

## API-Specific Issues

### LUT Not Appearing After Installation

**Problem:** LUT installed but not visible in DaVinci Resolve.

**Solution:**

1. **Refresh LUT list manually:**
   - In Resolve, go to Color page
   - Right-click on any node
   - The LUT should now appear in the list

2. **Check LUT file format:**
   - Supported formats: `.cube`, `.3dl`, `.lut`
   - Verify file is not corrupted
   - Try opening LUT file in text editor to check format

3. **Verify installation location:**
   ```bash
   # macOS
   ls "/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"

   # Windows
   dir "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT"
   ```

### SetLUT() Returns False

**Problem:** `clip.SetLUT()` fails silently.

**Possible Causes:**

1. **Node doesn't exist:**
   - API cannot create nodes
   - Ensure node exists before applying LUT
   - Use DRX template to create node structure first

2. **LUT filename incorrect:**
   - Use filename only, not full path: `"my_lut.cube"` not `"/path/to/my_lut.cube"`
   - Check spelling and case sensitivity

3. **Node index out of range:**
   ```bash
   # Check how many nodes exist
   python3 Scripts/Utilities/timeline_analyzer.py --detailed
   ```

### Metadata Not Saving

**Problem:** SetMetadata() appears to succeed but changes don't persist.

**Solution:**

1. **Different API for timeline vs media pool:**
   - MediaPoolItem: `clip.SetMetadata(field, value)`
   - TimelineItem: `clip.SetMetadata({field: value})`
   - Our scripts handle this automatically

2. **Field name typos:**
   - Use exact field names: `"Scene"`, `"Shot"`, `"Take"`
   - Case-sensitive

3. **Verify after setting:**
   ```bash
   # Check if metadata was set
   python3 Scripts/Utilities/metadata_manager.py --list
   ```

### Render Jobs Not Starting

**Problem:** Render queue populated but rendering doesn't start.

**Solution:**

1. **Check render settings:**
   - Ensure output directory exists and has write permissions
   - Verify codec is available in your Resolve version

2. **Manually trigger render:**
   ```bash
   python3 Scripts/Utilities/render_manager.py --start
   ```

3. **Check Resolve UI:**
   - Open Deliver page
   - Check for error messages in render queue

---

## Platform-Specific Issues

### macOS: "Operation not permitted"

**Problem:** macOS security prevents script execution.

**Solution:**

1. **Grant terminal permissions:**
   - System Preferences → Security & Privacy → Privacy
   - Grant "Full Disk Access" or "Automation" to Terminal/iTerm

2. **For LUT installation:**
   ```bash
   sudo python3 Scripts/Utilities/lut_installer.py my_lut.cube
   ```

### Windows: "fusionscript.dll not found"

**Problem:** Cannot locate DaVinci Resolve library on Windows.

**Solution:**

1. **Verify installation path:**
   ```cmd
   dir "C:\Program Files\Blackmagic Design\DaVinci Resolve"
   ```

2. **Update RESOLVE_SCRIPT_LIB:**
   ```cmd
   # If installed in custom location
   set RESOLVE_SCRIPT_LIB=D:\Custom\Path\DaVinci Resolve\fusionscript.dll
   ```

### Linux: API Files Not Found

**Problem:** API files missing on Linux installation.

**Solution:**

1. **Check common installation locations:**
   ```bash
   find /opt -name "fusionscript.so" 2>/dev/null
   find ~ -name "fusionscript.so" 2>/dev/null
   ```

2. **Install API files if missing:**
   - May need to download from Blackmagic Design website
   - Copy to appropriate directory

---

## Performance Issues

### Script Runs Slowly

**Problem:** Script takes a long time to execute.

**Solution:**

1. **For large media pools:**
   ```bash
   # Use specific targeting instead of --all
   python3 batch_grade_apply.py --lut film.cube --node 4 --track 1
   ```

2. **For timeline analysis:**
   ```bash
   # Skip detailed mode if not needed
   python3 Scripts/Utilities/timeline_analyzer.py
   # Instead of
   python3 Scripts/Utilities/timeline_analyzer.py --detailed
   ```

3. **For metadata export:**
   ```bash
   # Skip properties if not needed
   python3 Scripts/Utilities/metadata_manager.py --export output.csv
   # Instead of
   python3 Scripts/Utilities/metadata_manager.py --export output.csv --properties
   ```

### Memory Issues with Large Projects

**Problem:** Script crashes or system runs out of memory.

**Solution:**

1. **Process in batches:**
   ```bash
   # Process one track at a time
   python3 batch_grade_apply.py --lut film.cube --node 4 --track 1
   python3 batch_grade_apply.py --lut film.cube --node 4 --track 2
   ```

2. **Close other applications:**
   - DaVinci Resolve itself is memory-intensive
   - Close unnecessary programs before running scripts

---

## Getting Help

If your issue is not covered here:

1. **Check script help:**
   ```bash
   python3 Scripts/Utilities/script_name.py --help
   ```

2. **Review documentation:**
   - [API Reference](API_Reference.md)
   - [Limitations](Limitations.md)
   - [Best Practices](Best_Practices.md)

3. **Report issues:**
   - [GitHub Issues](https://github.com/nobphotographr/davinci-resolve-automation/issues)
   - Include:
     - Operating system and version
     - DaVinci Resolve version
     - Python version
     - Full error message
     - Steps to reproduce

4. **Community resources:**
   - [Blackmagic Forum - Scripting](https://forum.blackmagicdesign.com/viewforum.php?f=21)
   - DaVinci Resolve scripting community

---

## Quick Diagnostic Checklist

Use this checklist to diagnose most issues:

- [ ] DaVinci Resolve is running
- [ ] DaVinci Resolve Studio version (not free)
- [ ] Project is open
- [ ] Timeline is open (if required)
- [ ] Environment variables are set (`echo $RESOLVE_SCRIPT_API`)
- [ ] Python 3.6+ is installed (`python3 --version`)
- [ ] Script has correct permissions (`chmod +x script.py` on macOS/Linux)
- [ ] Clips exist that match your criteria
- [ ] Required nodes exist (for LUT/CDL operations)
- [ ] Output directories exist and are writable

If all checks pass and issue persists, see "Getting Help" section above.
