# Release Checklist for Plantos MCP Installer v1.0.0

## ✅ Completed

### 1. Installer Development
- [x] Built GUI installer with Tkinter
- [x] Implemented OAuth device flow authentication
- [x] Added automatic AI assistant detection (Claude Desktop, ChatGPT)
- [x] Created local MCP server installation
- [x] Implemented config file updating
- [x] Fixed UI display issues (window sizing, text visibility)
- [x] Built unsigned installer successfully (113MB arm64)

### 2. MCP Download Page
- [x] Updated page.tsx to use Sprout icon from lucide-react
- [x] Consistent branding with homepage

### 3. Build Infrastructure
- [x] Created build.py script with PyInstaller
- [x] Fixed universal2 binary issues
- [x] Fixed icon file handling
- [x] Added support for code signing and notarization

### 4. CI/CD Setup
- [x] Created GitHub Actions workflow (`.github/workflows/build-installers.yml`)
- [x] Configured multi-platform builds (macOS, Windows, Linux)
- [x] Fixed MCP server path issues in workflow
- [x] Added DMG creation for macOS
- [x] Set up automatic GitHub release creation

### 5. Documentation
- [x] Created comprehensive code signing setup guide (`CODESIGNING_SETUP.md`)
- [x] Documented all required GitHub secrets
- [x] Added troubleshooting section
- [x] Created BUILD.md with build instructions

## 🔨 In Progress

### 6. GitHub Secrets Configuration (MANUAL STEP REQUIRED)

You need to add the following secrets to your GitHub repository:
**Location:** `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

#### Required Secrets:

1. **APPLE_CERTIFICATE_BASE64**
   - Your Developer ID certificate exported as base64
   - See CODESIGNING_SETUP.md Step 3.1 for instructions

2. **APPLE_CERTIFICATE_PASSWORD**
   - Password for your .p12 certificate

3. **KEYCHAIN_PASSWORD**
   - Any secure password for temporary build keychain

4. **APPLE_DEVELOPER_ID**
   - Format: `Developer ID Application: Your Name (TEAM_ID)`

5. **APPLE_ID**
   - Your Apple ID email

6. **APPLE_ID_PASSWORD**
   - App-specific password (NOT your Apple ID password)
   - Generate at https://appleid.apple.com/account/manage

7. **TEAM_ID**
   - Your 10-character Apple Developer Team ID

**Windows (Optional):**
8. **WINDOWS_CERTIFICATE_BASE64**
9. **WINDOWS_CERTIFICATE_PASSWORD**

**📖 Detailed Instructions:** See `CODESIGNING_SETUP.md`

## 📋 Pending

### 7. Sprout Icon Integration
- [ ] Install Cairo library: `brew install cairo`
- [ ] Convert sprout_icon.svg to PNG
- [ ] Integrate icon into Tkinter installer
- [ ] Update build.py with `--icon` flag

### 8. Create v1.0.0 Release
- [ ] Complete GitHub secrets setup (Step 6)
- [ ] Commit all changes
- [ ] Create and push release tag:
  ```bash
  cd /Users/tylerdennis/plantos/mcp-installer
  git add .
  git commit -m "feat: Prepare v1.0.0 release with signed installers"
  git tag v1.0.0
  git push origin main
  git push origin v1.0.0
  ```
- [ ] Monitor GitHub Actions build
- [ ] Verify signed installers in GitHub Release

### 9. Testing
- [ ] Download signed installers from GitHub Release
- [ ] Test macOS installer on clean Mac
- [ ] Verify code signature: `codesign -vvv --deep --strict PlantosMCPInstaller.app`
- [ ] Verify notarization: `spctl -a -vvv -t install PlantosMCPInstaller.app`
- [ ] Test complete installation flow
- [ ] Verify Claude Desktop integration works

### 10. User Documentation
- [ ] Create user guide for installer
- [ ] Add download instructions to plantos.co
- [ ] Update MCP download page with installer links
- [ ] Create troubleshooting FAQ
- [ ] Add screenshots/video walkthrough

## 🚀 Release Steps

### Phase 1: Pre-Release (Current)
1. ✅ Build and test unsigned installer locally
2. 🔨 Configure GitHub secrets
3. ⏳ Test manual workflow run

### Phase 2: Release
4. ⏳ Tag v1.0.0 and push
5. ⏳ Monitor GitHub Actions build
6. ⏳ Verify signed installers

### Phase 3: Post-Release
7. ⏳ Test installers on clean machines
8. ⏳ Update website with download links
9. ⏳ Announce release
10. ⏳ Monitor for issues

## 📝 Files Created/Modified in This Session

### New Files:
- `CODESIGNING_SETUP.md` - Complete code signing guide
- `RELEASE_CHECKLIST.md` - This file
- `sprout_icon.svg` - Sprout icon for future use

### Modified Files:
- `installer.py` - Fixed UI sizing and text visibility
- `build.py` - Fixed universal2 and icon issues
- `.github/workflows/build-installers.yml` - Fixed MCP server paths
- `farming-advisor-ui/src/app/mcp/download/page.tsx` - Added Sprout icon

## 🎯 Next Immediate Action

**You should now:**

1. **Read CODESIGNING_SETUP.md** to understand the code signing process
2. **Obtain your Apple Developer ID certificate** (if you don't have one)
3. **Follow Step 4 in CODESIGNING_SETUP.md** to add all 7 required secrets to GitHub
4. **Test with a manual workflow run** before creating the official release

Once secrets are configured, creating the release is as simple as:
```bash
git tag v1.0.0 && git push origin v1.0.0
```

GitHub Actions will handle the rest!

## 📞 Support

If you encounter issues:
- Check BUILD.md for build troubleshooting
- Check CODESIGNING_SETUP.md for signing issues
- Review GitHub Actions logs for CI/CD problems
