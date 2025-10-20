# Plantos MCP Desktop Installer

One-click installer to connect Plantos agricultural intelligence to Claude Desktop using OAuth authorization.

## Features

- 🔐 **Secure OAuth Flow**: No manual API key copying needed
- 🎨 **Native GUI**: Beautiful tkinter interface
- 🔄 **Auto-Configuration**: Automatically sets up Claude Desktop
- 🌍 **Cross-Platform**: Works on macOS, Windows, and Linux
- 📦 **Single Binary**: No Python installation required

## For Users

### Download

Get the latest installer from [GitHub Releases](https://github.com/YOUR_USERNAME/mcp-server/releases):

- **macOS**: Download `plantos-mcp-installer-macos.zip`
- **Windows**: Download `plantos-mcp-installer-windows.zip`
- **Linux**: Download `plantos-mcp-installer-linux.tar.gz`

### Installation

1. Download the appropriate installer for your platform
2. Extract and run the installer
3. Click "Install Plantos MCP"
4. Your browser will open to authorize the connection
5. Log in to your Plantos account (or create one)
6. Restart Claude Desktop

That's it! Plantos tools are now available in Claude Desktop.

## For Developers

### Building from Source

#### Prerequisites

- Python 3.11+
- pip

#### macOS / Linux

```bash
# Install dependencies
pip install pyinstaller

# Build
chmod +x build.sh
./build.sh

# Test
open "dist/Plantos MCP Installer.app"  # macOS
./dist/plantos-mcp-installer           # Linux
```

#### Windows

```cmd
rem Install dependencies
pip install pyinstaller

rem Build
build.bat

rem Test
dist\plantos-mcp-installer.exe
```

### Creating a Release

1. Tag a new version:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. GitHub Actions will automatically:
   - Build for all platforms
   - Create a GitHub Release
   - Attach all binaries

### OAuth Flow

The installer implements an OAuth device flow:

1. **Request Code**: Installer calls `POST /api/v1/mcp/request-code`
2. **User Authorization**: Browser opens to `/mcp/authorize?code=XXXX-XXXX`
3. **Poll for Token**: Installer polls `GET /api/v1/mcp/check-code`
4. **Configure**: API key is saved to Claude Desktop config

### Project Structure

```
mcp-server/
├── installer.py              # Main installer GUI
├── installer.spec            # PyInstaller configuration
├── build.sh                  # macOS/Linux build script
├── build.bat                 # Windows build script
├── src/
│   └── plantos_mcp_server.py # MCP server implementation
└── .github/
    └── workflows/
        └── release.yml       # Auto-build workflow
```

### Configuration

The installer configures Claude Desktop by modifying:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

It adds:

```json
{
  "mcpServers": {
    "plantos": {
      "command": "python",
      "args": ["/path/to/plantos_mcp_server.py"],
      "env": {
        "PLANTOS_API_URL": "https://api.plantos.co",
        "PLANTOS_API_KEY": "plantos_xxxxx"
      }
    }
  }
}
```

## Troubleshooting

### macOS: "App is damaged and can't be opened"

This happens because the app isn't signed. Run:

```bash
xattr -cr "Plantos MCP Installer.app"
open "Plantos MCP Installer.app"
```

### Windows: "Windows protected your PC"

Click "More info" → "Run anyway"

### Linux: Permission denied

```bash
chmod +x plantos-mcp-installer
./plantos-mcp-installer
```

### Authorization code expired

Codes expire after 5 minutes. Close the installer and start fresh.

## License

MIT License - See LICENSE file for details

## Support

- Documentation: [plantos.co/docs](https://plantos.co/docs)
- Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/mcp-server/issues)
- Email: support@plantos.co
