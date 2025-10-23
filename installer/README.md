# Plantos MCP Installer

One-click installer for configuring Claude Desktop and ChatGPT to use Plantos MCP server.

## What It Does

1. **Authenticates** - Signs user into their Plantos account via OAuth
2. **Fetches API Key** - Retrieves user's Plantos API key
3. **Detects AI Assistants** - Finds Claude Desktop / ChatGPT installations
4. **Auto-Configures** - Updates config files with MCP settings
5. **Done!** - User just needs to restart their AI assistant

## Development

### Setup

```bash
cd plantos/mcp-installer
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Installer (Development)

```bash
python installer.py
```

### Test Individual Modules

```bash
# Test config detection
python config_editor.py

# Test authentication
python auth.py
```

### Build Executable

```bash
python build.py
```

Output will be in `dist/PlantosM CPInstaller` (or `.exe` on Windows)

## Architecture

Uses **OAuth Device Flow** (similar to smart TV apps):

```
User clicks "Sign In"
         ↓
Installer requests authorization code from API
         ↓
API generates code (e.g., "FARM-X7K9")
         ↓
Browser opens to plantos.co/mcp/authorize?code=FARM-X7K9
         ↓
User logs in (or signs up) and sees authorization page
         ↓
User clicks "Authorize"
         ↓
API marks code as authorized with user's API key
         ↓
Installer polls API and receives API key
         ↓
Installer scans for Claude/ChatGPT config files
         ↓
Installer updates config with:
{
  "mcpServers": {
    "plantos": {
      "url": "http://mcp.plantos.co:8080",
      "transport": {
        "type": "http",
        "headers": {
          "X-API-Key": "user-api-key"
        }
      }
    }
  }
}
         ↓
User restarts AI assistant
         ↓
Done! ✅
```

## Backend Requirements

**All backend infrastructure already implemented!**

The installer uses existing API endpoints:

### `POST /api/v1/mcp/request-code`

Generates authorization code for device flow.

**Returns:**
```json
{
  "code": "FARM-X7K9",
  "verification_url": "https://plantos.co/mcp/authorize?code=FARM-X7K9",
  "expires_in": 300
}
```

### `POST /api/v1/mcp/authorize`

User authorizes code after login (called by web UI, not installer).

**Body:**
```json
{
  "code": "FARM-X7K9"
}
```

**Headers:**
- `Authorization: Bearer {jwt_token}`

### `GET /api/v1/mcp/check-code?code=FARM-X7K9`

Installer polls this to check if user authorized.

**Returns:**
```json
{
  "status": "authorized",
  "api_key": "plantos_xxx..."
}
```

Or if still pending:
```json
{
  "status": "pending"
}
```

## Distribution

### macOS
- Build universal binary (Intel + Apple Silicon)
- Sign with Apple Developer cert (future)
- Notarize for macOS Gatekeeper (future)
- Distribute as `.app` or `.dmg`

### Windows
- Build `.exe` with PyInstaller
- Sign with code signing certificate (future)
- Distribute as `.exe` or `.msi` installer

### Linux
- Build AppImage or `.deb` package
- Distribute via package managers (future)

## Security Considerations

1. **OAuth Device Flow** - Uses standard OAuth 2.0 device flow (RFC 8628)
2. **No Localhost Server** - No callback server needed (more secure than redirect flow)
3. **HTTPS** - All communication with api.plantos.co over HTTPS
4. **Code Expiration** - Authorization codes expire after 5 minutes
5. **No Storage** - API key written directly to config, not stored by installer
6. **Subscription Required** - Users must have active Plantos subscription
7. **Single Use Codes** - Authorization codes can only be used once

## Future Enhancements

- [ ] Add app icon
- [ ] Support ChatGPT Desktop (when released)
- [ ] Auto-update functionality
- [ ] Uninstall/remove option
- [ ] Multi-language support
- [ ] Better error handling and logging
- [ ] Crash reporting
- [ ] Analytics (with consent)

## License

Proprietary - Plantos, Inc.
