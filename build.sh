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

# Code signing for macOS
if [ "$(uname)" == "Darwin" ]; then
    APP_PATH="dist/Plantos MCP Installer.app"

    # Check if a signing identity is available
    IDENTITY="${CODESIGN_IDENTITY:-Developer ID Application: Tyler Dennis (66872JU2N9)}"

    if security find-identity -v -p codesigning | grep -q "$IDENTITY"; then
        echo ""
        echo "🔐 Code signing macOS app..."

        # Sign all binaries and frameworks inside the app
        find "$APP_PATH/Contents/MacOS" -type f -perm +111 -exec codesign --force --deep --sign "$IDENTITY" --timestamp --options runtime {} \;

        # Sign the entire app bundle
        codesign --force --deep --sign "$IDENTITY" --timestamp --options runtime "$APP_PATH"

        # Verify the signature
        echo "Verifying signature..."
        codesign --verify --deep --strict --verbose=2 "$APP_PATH"

        echo "✅ Code signing complete!"
    else
        echo ""
        echo "⚠️  No valid signing identity found - app will not be signed"
        echo "   Identity needed: $IDENTITY"
        echo "   Users will need to right-click → Open to run the app"
    fi
fi

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
