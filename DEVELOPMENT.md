# Development & Deployment Guide

This guide covers the development workflow, release process, and infrastructure setup for the Plantos MCP Server.

## Table of Contents
- [Development Setup](#development-setup)
- [Release Process](#release-process)
- [Code Signing (macOS)](#code-signing-macos)
- [GitHub Actions](#github-actions)

---

## Development Setup

### Prerequisites
- Python 3.10+
- PyInstaller for building installers
- (macOS only) Developer ID Application certificate for code signing

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run installer locally (for testing)
python installer.py

# Build installer
./build.sh  # macOS/Linux
build.bat   # Windows
```

---

## Release Process

Releases are automatically created via GitHub Actions when you push a version tag.

### Creating a New Release

1. **Update version numbers** (if needed):
   - `smithery.yaml` and `smithery.json`
   - `pyproject.toml`
   - Any hardcoded version strings

2. **Commit changes**:
   ```bash
   git add .
   git commit -m "chore: Bump version to X.Y.Z"
   git push origin main
   ```

3. **Create and push version tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z: Description of changes"
   git push origin vX.Y.Z
   ```

4. **Monitor the build**:
   - Go to https://github.com/Plantos-Sensor/mcp-server/actions
   - Watch the "Build and Release MCP Installer" workflow
   - Builds take ~5-10 minutes

5. **Verify the release**:
   - Check https://github.com/Plantos-Sensor/mcp-server/releases
   - Download and test each platform's installer
   - Verify code signing on macOS (no Gatekeeper warning)

### Release Artifacts

Each release includes:
- `plantos-mcp-installer-macos.zip` - Signed macOS app bundle
- `plantos-mcp-installer-windows.zip` - Windows executable
- `plantos-mcp-installer-linux.tar.gz` - Linux binary

---

## Code Signing (macOS)

The macOS installer is automatically code-signed during the GitHub Actions build process to avoid Gatekeeper warnings.

### Required Setup

**1. Apple Developer Account**
- Enroll in the Apple Developer Program ($99/year)
- URL: https://developer.apple.com/programs/

**2. Create Developer ID Application Certificate**

On your Mac:
1. Open **Keychain Access**
2. Go to **Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority**
3. Fill in:
   - User Email: Your Apple ID
   - Common Name: "Plantos MCP Developer"
   - Request: "Saved to disk"
   - ✓ Check "Let me specify key pair information"
4. Save the `.certSigningRequest` file
5. Key settings: 2048 bits, RSA

In Apple Developer Portal:
1. Go to https://developer.apple.com/account/resources/certificates/list
2. Click **+** to create new certificate
3. Select **Developer ID Application** under Software
4. Choose **G2 Sub-CA** (for Xcode 11.4.1+)
5. Upload your `.certSigningRequest` file
6. Download the certificate (`.cer` file)
7. Double-click to install in Keychain

**3. Install Intermediate Certificate**

Download and install Apple's G2 intermediate certificate:
```bash
curl -o DeveloperIDG2CA.cer https://www.apple.com/certificateauthority/DeveloperIDG2CA.cer
open DeveloperIDG2CA.cer
```
Select **System** keychain when prompted.

**4. Export Certificate for GitHub Actions**

1. Open Keychain Access
2. Find "Developer ID Application: Your Name (TEAM_ID)"
3. Expand the triangle to show private key
4. Select both certificate and private key (Shift+Click)
5. Right-click → "Export 2 items..."
6. Save as `.p12` file with a password
7. Convert to base64:
   ```bash
   base64 -i certificate.p12 | pbcopy
   ```

**5. Add GitHub Secrets**

Go to https://github.com/Plantos-Sensor/mcp-server/settings/secrets/actions

Add these secrets:
- `MACOS_CERTIFICATE` - Base64-encoded .p12 file (paste from clipboard)
- `MACOS_CERTIFICATE_PASSWORD` - Password you set when exporting
- `APPLE_TEAM_ID` - Your Team ID (10-character code from certificate name)

### Verifying Code Signing

After a release is built, verify the signature:
```bash
# Download and unzip the release
curl -L -o installer.zip https://github.com/Plantos-Sensor/mcp-server/releases/latest/download/plantos-mcp-installer-macos.zip
unzip installer.zip

# Check signature
codesign -vv --deep --strict "Plantos MCP Installer.app"

# Should show:
# "Plantos MCP Installer.app: valid on disk"
# "Plantos MCP Installer.app: satisfies its Designated Requirement"
```

### Local Code Signing

If you have a certificate installed locally, `build.sh` will automatically sign the app:
```bash
./build.sh
# Should see: "🔐 Code signing macOS app..."
```

The script looks for identity: `Developer ID Application: Tyler Dennis (66872JU2N9)`

You can override with:
```bash
CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)" ./build.sh
```

---

## GitHub Actions

### Workflows

**`.github/workflows/release.yml`** - Build and Release Installer

Triggers:
- Push of version tags (`v*.*.*`)
- Manual workflow dispatch

Build matrix:
- macOS (latest) - Builds, signs, and packages `.app`
- Windows (latest) - Builds and packages `.exe`
- Linux (Ubuntu) - Builds and packages binary

Process:
1. Checkout code
2. Set up Python 3.11
3. Install PyInstaller
4. **(macOS only)** Import code signing certificate into temporary keychain
5. Build installer with PyInstaller
6. **(macOS only)** Code sign app bundle
7. **(macOS only)** Clean up temporary keychain
8. Package installer (zip/tar.gz)
9. Upload artifacts
10. Create GitHub release with all platform installers

### Required GitHub Secrets

| Secret | Purpose | How to Get |
|--------|---------|------------|
| `MACOS_CERTIFICATE` | Code signing certificate | Export .p12 and base64 encode |
| `MACOS_CERTIFICATE_PASSWORD` | Password for .p12 file | Set when exporting certificate |
| `APPLE_TEAM_ID` | Apple Developer Team ID | Found in certificate name (e.g., 66872JU2N9) |

### Troubleshooting Builds

**Build fails on macOS?**
- Check that all 3 GitHub secrets are set correctly
- Verify certificate is not expired in Apple Developer portal
- Check Actions logs for specific codesign errors

**Certificate import fails?**
- Ensure `MACOS_CERTIFICATE` is base64-encoded correctly (no line breaks)
- Verify `MACOS_CERTIFICATE_PASSWORD` matches export password
- Check that certificate includes private key (must export both)

**Signing succeeds but Gatekeeper still blocks?**
- Certificate must be "Developer ID Application" (not "Apple Development")
- Must be G2 certificate (not legacy)
- App must be distributed as zip (not directly)
- Users should download from GitHub (not via curl/wget which sets quarantine)

---

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Smithery.ai Registry](https://smithery.ai/)

---

## Support

For issues or questions:
- Open an issue: https://github.com/Plantos-Sensor/mcp-server/issues
- Email: support@plantos.co
- Website: https://plantos.co
