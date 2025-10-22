# Development & Deployment Guide

This guide covers the development workflow, release process, and infrastructure setup for the Plantos MCP Server.

## Table of Contents
- [Development Setup](#development-setup)
- [Installer Overview](#installer-overview)
- [Release Process](#release-process)
- [GitHub Actions](#github-actions)

---

## Development Setup

### Prerequisites
- Python 3.10+
- No special build tools required!

### Local Development

The installer is a simple shell script that:
1. Checks for Python 3
2. Calls the OAuth API to get an authorization code
3. Opens the user's browser for authorization
4. Polls for authorization completion
5. Installs `plantos-mcp` via pip
6. Configures Claude Desktop

To test locally:
```bash
# macOS/Linux
./install.sh

# Windows
.\install.bat
```

---

## Installer Overview

The Plantos MCP installer uses a script-based approach for simplicity and reliability.

### Why Scripts Instead of GUI Apps?

Previous versions used PyInstaller to create GUI applications, but this approach had fundamental issues with macOS code signing:
- PyInstaller bundles Python.framework with a different Team ID
- macOS Sequoia enforces strict code signing validation
- The bundled Python conflicted with our Developer ID certificate
- This is a known limitation of PyInstaller on modern macOS

The script-based approach:
- ✅ No code signing issues
- ✅ Industry standard for MCP servers
- ✅ Simple to maintain and debug
- ✅ Works across all platforms
- ✅ Reuses existing OAuth infrastructure
- ✅ Still provides a "double-click to install" experience

### Platform-Specific Files

**macOS:** `Install Plantos MCP.command`
- Double-clickable shell script (Terminal opens and runs it)
- No security warnings needed
- Same experience as an app for end users

**Windows:** `Install Plantos MCP.bat`
- Double-clickable batch file (Command Prompt opens and runs it)
- Built-in Windows functionality

**Linux:** `install-plantos-mcp.sh`
- Standard shell script
- Users run via terminal: `./install-plantos-mcp.sh`

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
   - Builds take ~1-2 minutes (much faster than PyInstaller!)

5. **Verify the release**:
   - Check https://github.com/Plantos-Sensor/mcp-server/releases
   - Download and test each platform's installer

### Release Artifacts

Each release includes:
- `plantos-mcp-installer-macos.zip` - Contains `Install Plantos MCP.command` and `install-plantos-mcp.sh`
- `plantos-mcp-installer-windows.zip` - Contains `Install Plantos MCP.bat`
- `plantos-mcp-installer-linux.tar.gz` - Contains `install-plantos-mcp.sh`

---

## GitHub Actions

### Workflows

**`.github/workflows/release.yml`** - Build and Release Installer

Triggers:
- Push of version tags (`v*.*.*`)
- Manual workflow dispatch

Build matrix:
- macOS (latest) - Packages shell scripts
- Windows (latest) - Packages batch file
- Linux (Ubuntu) - Packages shell script

Process:
1. Checkout code
2. Copy installer scripts with platform-specific names:
   - macOS: `Install Plantos MCP.command` and `install-plantos-mcp.sh`
   - Windows: `Install Plantos MCP.bat`
   - Linux: `install-plantos-mcp.sh`
3. Set executable permissions (Unix platforms)
4. Create archive (zip/tar.gz)
5. Upload artifacts
6. Create GitHub release with all platform installers

### Required GitHub Secrets

None! The script-based approach doesn't require any secrets or certificates.

### Troubleshooting Builds

**Build fails?**
- Check that `install.sh` and `install.bat` exist in the repository
- Verify GitHub Actions workflow syntax in `.github/workflows/release.yml`
- Check Actions logs for specific errors

**Scripts don't work after download?**
- Ensure executable permissions are set (Unix platforms)
- Windows users may need to "Unblock" the file in Properties
- macOS users may need to give Terminal permission to run scripts

---

## Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Smithery.ai Registry](https://smithery.ai/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)

---

## Support

For issues or questions:
- Open an issue: https://github.com/Plantos-Sensor/mcp-server/issues
- Email: support@plantos.co
- Website: https://plantos.co
