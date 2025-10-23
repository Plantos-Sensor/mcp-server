# Building Signed Installers

This document explains how to build signed, distributable installers for the Plantos MCP Installer.

## Prerequisites

### macOS
- Python 3.11+
- PyInstaller
- Apple Developer ID certificate
- macOS 10.15+ for notarization

### Windows
- Python 3.11+
- PyInstaller
- Code signing certificate
- Windows SDK (for signtool.exe)

### Linux
- Python 3.11+
- PyInstaller
- (Optional) appimagetool for AppImage creation

## Local Development Builds

### Unsigned Build (Any Platform)

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Copy MCP server files
cp -r ../mcp-server ./mcp-server

# Build
python build.py
```

Output: `dist/PlantosMCPInstaller.app` (macOS), `dist/PlantosMCPInstaller.exe` (Windows), or `dist/PlantosMCPInstaller` (Linux)

### Signed Build (macOS)

```bash
# Build with code signing
export APPLE_DEVELOPER_ID="Developer ID Application: Your Name (TEAM_ID)"
python build.py --sign

# Build with code signing AND notarization
export APPLE_ID="your-apple-id@email.com"
export APPLE_ID_PASSWORD="app-specific-password"
export TEAM_ID="YOUR_TEAM_ID"
export NOTARIZE="true"
python build.py --sign
```

## Automated Builds (GitHub Actions)

The repository includes a GitHub Actions workflow that automatically builds signed installers for all platforms.

### Required GitHub Secrets

#### macOS Code Signing
1. **APPLE_CERTIFICATE_BASE64** - Base64-encoded .p12 certificate
   ```bash
   base64 -i DeveloperID.p12 | pbcopy
   ```

2. **APPLE_CERTIFICATE_PASSWORD** - Password for .p12 certificate

3. **KEYCHAIN_PASSWORD** - Password for build keychain (can be any value)

4. **APPLE_DEVELOPER_ID** - Your code signing identity
   ```
   Developer ID Application: Company Name (TEAM_ID)
   ```

#### macOS Notarization
5. **APPLE_ID** - Your Apple ID email
   ```
   your-apple-id@email.com
   ```

6. **APPLE_ID_PASSWORD** - App-specific password (NOT your Apple ID password)
   - Generate at https://appleid.apple.com/account/manage
   - Select "App-Specific Passwords"

7. **TEAM_ID** - Your Apple Developer Team ID
   - Find at https://developer.apple.com/account

#### Windows Code Signing
8. **WINDOWS_CERTIFICATE_BASE64** - Base64-encoded .pfx certificate
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("certificate.pfx")) | Set-Clipboard
   ```

9. **WINDOWS_CERTIFICATE_PASSWORD** - Password for .pfx certificate

### Workflow Triggers

The workflow runs on:
- **Push to main** - Builds unsigned installers
- **Tags (v\*)** - Builds signed installers and creates GitHub release
- **Pull requests** - Builds unsigned installers for testing
- **Manual trigger** - Use "Run workflow" button in Actions tab

### Creating a Release

1. Tag a release:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions will:
   - Build signed installers for macOS, Windows, and Linux
   - Notarize the macOS app
   - Create DMG for macOS
   - Create GitHub release
   - Attach all installers to the release

## Code Signing Setup

### macOS

#### 1. Get Developer ID Certificate

1. Join Apple Developer Program ($99/year)
2. Go to https://developer.apple.com/account/resources/certificates
3. Create "Developer ID Application" certificate
4. Download and install in Keychain

#### 2. Export Certificate

```bash
# Open Keychain Access
# Find "Developer ID Application: Your Name"
# Right-click → Export
# Save as .p12 with a password
```

#### 3. Get Team ID

```bash
# Find your Team ID
security find-identity -v -p codesigning
```

Look for: `Developer ID Application: Your Name (TEAM_ID)`

#### 4. Create App-Specific Password

1. Go to https://appleid.apple.com/account/manage
2. Security → App-Specific Passwords
3. Generate new password
4. Save it securely

### Windows

#### 1. Get Code Signing Certificate

Purchase from:
- DigiCert
- Sectigo
- GlobalSign
- Other trusted CA

#### 2. Export Certificate

1. Install certificate in Windows
2. Open Certificate Manager (certmgr.msc)
3. Find your certificate
4. Right-click → All Tasks → Export
5. Export as .pfx with password

### Linux

No code signing required for Linux builds.

## Entitlements (macOS)

The `entitlements.plist` file grants necessary permissions for the app:

- **JIT compilation** - Required for Python runtime
- **Unsigned executable memory** - Required for Python packages
- **DYLD environment variables** - Required for Python imports
- **Disable library validation** - Required for third-party packages
- **Network client** - Required for API calls
- **File access** - Required for config file updates

## Troubleshooting

### macOS: "App is damaged and can't be opened"

This happens when the app isn't properly signed or notarized.

**Solution:**
```bash
# For testing only - disable Gatekeeper temporarily
sudo xattr -r -d com.apple.quarantine /path/to/PlantosMCPInstaller.app
```

For distribution, ensure the app is properly signed and notarized.

### Windows: "Windows protected your PC"

This happens when the exe isn't signed with a trusted certificate.

**Solution:**
- Sign with EV (Extended Validation) certificate for immediate trust
- Standard certificates gain trust after enough installs
- Users can click "More info" → "Run anyway"

### Code Signing Failed: "identity not found"

**Solution:**
```bash
# List available identities
security find-identity -v -p codesigning

# Use the exact identity string
python build.py --sign --identity "Developer ID Application: Your Name (TEAM_ID)"
```

### Notarization Failed

Check notarization log:
```bash
xcrun notarytool log <submission-id> --apple-id <apple-id> --password <password> --team-id <team-id>
```

Common issues:
- Hardened runtime not enabled → Fixed in build.py
- Missing entitlements → Check entitlements.plist
- Unsigned frameworks → Use `--deep` flag (already in build.py)

## Distribution

### macOS
- **DMG** - Recommended for direct download
- **PKG** - Alternative installer format
- **Homebrew Cask** - For package manager distribution
- **Mac App Store** - Requires separate signing process

### Windows
- **EXE** - Direct download (current)
- **MSI** - Windows Installer format (planned)
- **Microsoft Store** - Future consideration
- **Chocolatey** - For package manager distribution

### Linux
- **Raw binary** - Direct download (current)
- **AppImage** - Portable format (planned)
- **DEB** - Debian/Ubuntu packages (planned)
- **RPM** - Red Hat/Fedora packages (planned)
- **Snap/Flatpak** - Universal packages (future)

## Security Considerations

1. **Certificate Protection**
   - Store certificates securely
   - Never commit certificates to git
   - Use GitHub Secrets for CI/CD
   - Rotate app-specific passwords regularly

2. **Build Verification**
   - Verify signatures after build
   - Test installers on clean VMs
   - Check notarization status

3. **Distribution**
   - Host installers on HTTPS
   - Provide SHA256 checksums
   - Sign checksums file

## Resources

- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Apple Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Windows Code Signing](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
