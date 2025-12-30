#!/bin/bash

# DaVinci Resolve Automation Setup Script
# Supports: macOS, Linux

set -e

echo "=========================================="
echo "DaVinci Resolve Automation Setup"
echo "=========================================="
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    PLATFORM="macOS";;
    Linux*)     PLATFORM="Linux";;
    *)          PLATFORM="UNKNOWN";;
esac

echo "Detected platform: ${PLATFORM}"
echo ""

# Set platform-specific paths
if [ "$PLATFORM" = "macOS" ]; then
    RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    LUT_DIR="/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
    SHELL_RC="$HOME/.zshrc"
elif [ "$PLATFORM" = "Linux" ]; then
    RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
    RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
    LUT_DIR="$HOME/.local/share/DaVinciResolve/LUT"
    SHELL_RC="$HOME/.bashrc"
else
    echo "❌ Unsupported platform: ${OS}"
    echo "This script supports macOS and Linux only."
    echo "For Windows, please run setup.bat instead."
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Checking DaVinci Resolve installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if DaVinci Resolve is installed
if [ ! -d "$RESOLVE_SCRIPT_API" ]; then
    echo "⚠️  Warning: DaVinci Resolve API not found at:"
    echo "   $RESOLVE_SCRIPT_API"
    echo ""
    echo "Please install DaVinci Resolve Studio before running this script."
    echo "Note: Free version has limited API access."
    exit 1
fi

echo "✅ DaVinci Resolve installation found"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Setting up environment variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if environment variables are already set in shell RC file
if grep -q "RESOLVE_SCRIPT_API" "$SHELL_RC" 2>/dev/null; then
    echo "✅ Environment variables already configured in $SHELL_RC"
else
    echo "Adding environment variables to $SHELL_RC..."

    cat >> "$SHELL_RC" << EOF

# DaVinci Resolve Python API
export RESOLVE_SCRIPT_API="$RESOLVE_SCRIPT_API"
export RESOLVE_SCRIPT_LIB="$RESOLVE_SCRIPT_LIB"
export PYTHONPATH="\$PYTHONPATH:\$RESOLVE_SCRIPT_API/Modules"
EOF

    echo "✅ Environment variables added to $SHELL_RC"
    echo ""
    echo "ℹ️  Note: Restart your terminal or run:"
    echo "   source $SHELL_RC"
fi

# Set for current session
export RESOLVE_SCRIPT_API="$RESOLVE_SCRIPT_API"
export RESOLVE_SCRIPT_LIB="$RESOLVE_SCRIPT_LIB"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules"

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Installing sample LUTs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create LUT directory if it doesn't exist
if [ ! -d "$LUT_DIR" ]; then
    echo "Creating LUT directory: $LUT_DIR"
    mkdir -p "$LUT_DIR"
fi

# Copy sample LUTs
if [ -d "Examples/LUT" ]; then
    LUT_COUNT=$(find Examples/LUT -name "*.cube" | wc -l | tr -d ' ')

    if [ "$LUT_COUNT" -gt 0 ]; then
        echo "Copying $LUT_COUNT sample LUT(s) to $LUT_DIR..."

        for lut in Examples/LUT/*.cube; do
            if [ -f "$lut" ]; then
                lut_name=$(basename "$lut")
                cp "$lut" "$LUT_DIR/"
                echo "  ✅ $lut_name"
            fi
        done

        echo ""
        echo "✅ Sample LUTs installed successfully"
    else
        echo "⚠️  No LUT files found in Examples/LUT/"
    fi
else
    echo "⚠️  Examples/LUT directory not found"
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Verifying Python installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION found"
else
    echo "❌ python3 not found"
    echo "Please install Python 3.6 or later"
    exit 1
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Testing DaVinci Resolve API connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test API connection
python3 << 'PYTHON_TEST'
import sys
import os

# Add API path
api_path = os.environ.get('RESOLVE_SCRIPT_API')
if api_path:
    sys.path.append(api_path + "/Modules")

try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")

    if resolve:
        print("✅ Successfully connected to DaVinci Resolve")

        # Get project manager
        pm = resolve.GetProjectManager()
        if pm:
            project = pm.GetCurrentProject()
            if project:
                print(f"✅ Current project: {project.GetName()}")
            else:
                print("ℹ️  No project is currently open")
                print("   Please open a project in DaVinci Resolve to test scripts")
        else:
            print("⚠️  Could not access Project Manager")
    else:
        print("❌ Could not connect to DaVinci Resolve")
        print("   Make sure DaVinci Resolve is running")
        sys.exit(1)

except ImportError as e:
    print(f"❌ Failed to import DaVinciResolveScript: {e}")
    print("   Check that RESOLVE_SCRIPT_API is set correctly")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYTHON_TEST

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  API connection test failed"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure DaVinci Resolve is running"
    echo "2. Make sure you have DaVinci Resolve Studio (not free version)"
    echo "3. Try restarting DaVinci Resolve"
    echo ""
    exit 1
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Summary:"
echo "  • Platform: $PLATFORM"
echo "  • Environment variables: Configured"
echo "  • Sample LUTs: Installed"
echo "  • API connection: Working"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Restart your terminal or run:"
echo "   source $SHELL_RC"
echo ""
echo "2. Open a project in DaVinci Resolve"
echo ""
echo "3. Try running a sample script:"
echo "   python3 Scripts/ColorGrading/lut_comparison.py"
echo ""
echo "4. Read the documentation:"
echo "   cat README.md"
echo "   cat Docs/Best_Practices.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
