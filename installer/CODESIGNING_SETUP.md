# Code Signing Setup Guide

This guide walks you through setting up code signing for the Plantos MCP Installer.

## Prerequisites

- Apple Developer Program membership ($99/year)
- Access to your GitHub repository settings
- macOS with Xcode command-line tools installed

## Step 1: Obtain Apple Developer ID Certificate

### 1.1 Create Certificate

1. Go to https://developer.apple.com/account/resources/certificates
2. Click the "+" button to create a new certificate
3. Select "Developer ID Application"
4. Follow the prompts to create and download the certificate
5. Double-click the downloaded certificate to install it in your Keychain

### 1.2 Export Certificate as .p12

```bash
# Open Keychain Access
open "/Applications/Utilities/Keychain Access.app"
```

1. In Keychain Access, search for "Developer ID Application"
2. Find your certificate (it will show your name and team ID)
3. Right-click on the certificate → "Export..."
4. Save as: `DeveloperID.p12`
5. Set a strong password when prompted
6. Save the file securely

### 1.3 Get Your Team ID

Your Team ID is shown in the certificate name:
```
Developer ID Application: Your Name (TEAM_ID)
```

You can also find it at:
```bash
# List all code signing identities
security find-identity -v -p codesigning
```

Or visit: https://developer.apple.com/account (under "Membership Details")

## Step 2: Create App-Specific Password

For notarization, you need an app-specific password (NOT your regular Apple ID password):

1. Go to https://appleid.apple.com/account/manage
2. Navigate to "Security" section
3. Under "App-Specific Passwords", click "Generate Password"
4. Label it: "Plantos MCP Installer Notarization"
5. Copy and save the generated password securely

## Step 3: Prepare Certificate for GitHub

### 3.1 Convert Certificate to Base64

```bash
# Navigate to where you saved DeveloperID.p12
cd ~/Downloads

# Convert to base64 and copy to clipboard
base64 -i DeveloperID.p12 | pbcopy

# The base64 string is now in your clipboard
```

## Step 4: Add GitHub Secrets

Go to your GitHub repository:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
```

Click "New repository secret" and add each of the following:

### macOS Code Signing Secrets

**1. APPLE_CERTIFICATE_BASE64**
- Value: Paste the base64 string from your clipboard (from Step 3.1)

**2. APPLE_CERTIFICATE_PASSWORD**
- Value: The password you set when exporting the .p12 certificate

**3. KEYCHAIN_PASSWORD**
- Value: Any secure password (e.g., use a password generator)
- This is used to create a temporary keychain during CI builds

**4. APPLE_DEVELOPER_ID**
- Value: Your full code signing identity string
- Format: `Developer ID Application: Your Name (TEAM_ID)`
- Example: `Developer ID Application: Plantos Inc (ABC123DEF4)`

### macOS Notarization Secrets

**5. APPLE_ID**
- Value: Your Apple ID email
- Example: `your-email@example.com`

**6. APPLE_ID_PASSWORD**
- Value: The app-specific password from Step 2
- This is NOT your regular Apple ID password!

**7. TEAM_ID**
- Value: Your 10-character Apple Developer Team ID
- Example: `ABC123DEF4`

### Windows Code Signing Secrets (Optional - for future)

**8. WINDOWS_CERTIFICATE_BASE64**
- Value: Base64-encoded .pfx certificate
- To generate:
  ```powershell
  [Convert]::ToBase64String([IO.File]::ReadAllBytes("certificate.pfx")) | Set-Clipboard
  ```

**9. WINDOWS_CERTIFICATE_PASSWORD**
- Value: Password for your .pfx certificate

## Step 5: Verify Setup

### 5.1 Test with Manual Workflow Run

1. Go to GitHub Actions tab in your repository
2. Select the "Build and Release" workflow
3. Click "Run workflow" dropdown
4. Select branch: `main`
5. Click "Run workflow"
6. Monitor the build logs to ensure signing and notarization succeed

### 5.2 Local Test (Optional)

Test signing locally before pushing to GitHub:

```bash
cd /Users/tylerdennis/plantos/mcp-installer

# Set environment variables
export APPLE_DEVELOPER_ID="Developer ID Application: Your Name (TEAM_ID)"

# Build with signing
python build.py --sign

# Build with signing AND notarization
export APPLE_ID="your-email@example.com"
export APPLE_ID_PASSWORD="your-app-specific-password"
export TEAM_ID="YOUR_TEAM_ID"
export NOTARIZE="true"
python build.py --sign
```

## Step 6: Create Release

Once secrets are configured:

```bash
# Tag a new release
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will automatically:
- Build signed installers for macOS, Windows, and Linux
- Notarize the macOS app with Apple
- Create a DMG for macOS distribution
- Create a GitHub Release
- Attach all installers to the release

## Troubleshooting

### "Certificate not found" Error

```bash
# List all available identities
security find-identity -v -p codesigning

# Make sure the identity string exactly matches what's in the certificate
```

### Notarization Failed

```bash
# Check notarization log
xcrun notarytool log <submission-id> \
  --apple-id your-email@example.com \
  --password your-app-specific-password \
  --team-id YOUR_TEAM_ID
```

Common issues:
- Wrong app-specific password (must generate new one, not reuse old)
- Hardened runtime not enabled (already configured in build.py)
- Missing entitlements (already configured in entitlements.plist)

### "App is damaged" Warning on macOS

This happens when:
1. App isn't signed
2. App isn't notarized
3. Gatekeeper quarantine attribute is set

For testing unsigned builds:
```bash
sudo xattr -r -d com.apple.quarantine /path/to/PlantosMCPInstaller.app
```

## Security Best Practices

1. **Never commit certificates or passwords to git**
2. **Use GitHub Secrets for all sensitive values**
3. **Rotate app-specific passwords periodically**
4. **Keep .p12 certificate file in secure storage**
5. **Use strong passwords for certificate export**

## Quick Reference

| Secret Name | Example Value | Where to Get It |
|-------------|---------------|-----------------|
| APPLE_CERTIFICATE_BASE64 | `MIIK...` (very long) | Export .p12 → base64 |
| APPLE_CERTIFICATE_PASSWORD | `MySecureP@ss123` | Password you set on export |
| KEYCHAIN_PASSWORD | `RandomStr0ng!Pass` | Generate any secure password |
| APPLE_DEVELOPER_ID | `Developer ID Application: Plantos Inc (ABC123)` | Keychain or developer.apple.com |
| APPLE_ID | `dev@plantos.co` | Your Apple ID email |
| APPLE_ID_PASSWORD | `abcd-efgh-ijkl-mnop` | appleid.apple.com → App-Specific |
| TEAM_ID | `ABC123DEF4` | developer.apple.com → Membership |

## Next Steps

After setting up code signing:

1. ✅ Test with manual workflow run
2. ✅ Create v1.0.0 release tag
3. ✅ Verify signed installers in GitHub Release
4. ✅ Download and test on clean Mac
5. ✅ Update download links on plantos.co

## Resources

- [Apple Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Apple Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
