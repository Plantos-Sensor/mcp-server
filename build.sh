#!/bin/bash
# Build Plantos MCP Installer for Mac/Linux

set -e

echo "🌾 Building Plantos MCP Installer..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the installer
echo "Building installer..."
pyinstaller installer.spec

echo ""
echo "✅ Build complete!"
echo ""

# Show output
if [ "$(uname)" == "Darwin" ]; then
    echo "📦 macOS App Bundle: dist/Plantos MCP Installer.app"
    echo ""
    echo "To test locally:"
    echo "  open 'dist/Plantos MCP Installer.app'"
    echo ""
    echo "To distribute:"
    echo "  1. Zip the app: cd dist && zip -r plantos-mcp-installer-macos.zip 'Plantos MCP Installer.app'"
    echo "  2. Upload to GitHub Releases"
else
    echo "📦 Linux Executable: dist/plantos-mcp-installer"
    echo ""
    echo "To test locally:"
    echo "  ./dist/plantos-mcp-installer"
    echo ""
    echo "To distribute:"
    echo "  1. Create tarball: cd dist && tar -czf plantos-mcp-installer-linux.tar.gz plantos-mcp-installer"
    echo "  2. Upload to GitHub Releases"
fi
