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

        # Sign the main executable (without --options runtime to allow embedded Python framework)
        codesign --force --sign "$IDENTITY" --timestamp "$APP_PATH/Contents/MacOS/plantos-mcp-installer"

        # Sign the entire app bundle (without hardened runtime due to PyInstaller's embedded frameworks)
        codesign --force --sign "$IDENTITY" --timestamp "$APP_PATH"

        # Verify the signature
        echo "Verifying signature..."
        codesign --verify --strict --verbose=2 "$APP_PATH"

        echo "✅ Code signing complete!"

        # Notarization (only if credentials are available)
        if [ ! -z "$APPLE_ID" ] && [ ! -z "$APPLE_APP_PASSWORD" ]; then
            echo ""
            echo "📝 Notarizing app with Apple..."

            # Create a zip for notarization
            NOTARIZE_ZIP="dist/Plantos-MCP-Installer-notarize.zip"
            ditto -c -k --keepParent "$APP_PATH" "$NOTARIZE_ZIP"

            # Submit for notarization
            echo "Submitting to Apple notarization service..."
            SUBMISSION_OUTPUT=$(xcrun notarytool submit "$NOTARIZE_ZIP" \
                --apple-id "$APPLE_ID" \
                --password "$APPLE_APP_PASSWORD" \
                --team-id "${APPLE_TEAM_ID:-66872JU2N9}" \
                --wait 2>&1)

            NOTARIZE_STATUS=$?
            echo "$SUBMISSION_OUTPUT"

            # Extract submission ID for log retrieval
            SUBMISSION_ID=$(echo "$SUBMISSION_OUTPUT" | grep "id:" | head -1 | awk '{print $2}')

            # Clean up zip
            rm "$NOTARIZE_ZIP"

            if [ $NOTARIZE_STATUS -eq 0 ]; then
                echo "Stapling notarization ticket to app..."
                if xcrun stapler staple "$APP_PATH" 2>&1; then
                    echo "✅ Notarization complete!"
                else
                    echo "⚠️  Stapling failed, but notarization succeeded"
                    echo "   The app is still notarized and will work"
                fi
            else
                echo ""
                echo "⚠️  Notarization failed - app is signed but not notarized"

                if [ ! -z "$SUBMISSION_ID" ]; then
                    echo "📋 Fetching notarization log..."
                    xcrun notarytool log "$SUBMISSION_ID" \
                        --apple-id "$APPLE_ID" \
                        --password "$APPLE_APP_PASSWORD" \
                        --team-id "${APPLE_TEAM_ID:-66872JU2N9}" 2>&1 || true
                fi

                echo ""
                echo "   The app is still signed and will work, but users will need to:"
                echo "   • Right-click → Open (first launch only)"
                echo "   • Or run: xattr -cr 'Plantos MCP Installer.app'"
            fi
        else
            echo ""
            echo "ℹ️  Skipping notarization (APPLE_ID or APPLE_APP_PASSWORD not set)"
            echo "   App is signed but not notarized"
            echo "   Users will need to right-click → Open on first launch"
        fi
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
