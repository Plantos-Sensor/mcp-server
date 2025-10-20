# Plantos MCP Server - Quick Start

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd mcp-server
./setup.sh
```

### 2. Configure Environment
```bash
# Edit .env with your settings
nano .env
```

Set these values:
```
PLANTOS_API_URL=http://localhost:8000
PLANTOS_API_KEY=test-key-local-dev
```

### 3. Start Plantos API (Terminal 1)
```bash
cd ../farming-advisor-api
python run.py
```

### 4. Test MCP Server (Terminal 2)
```bash
cd mcp-server
python src/plantos_mcp_server.py
```

### 5. Configure Claude Desktop

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "plantos": {
      "command": "python",
      "args": [
        "/Users/tylerdennis/plantos/mcp-server/src/plantos_mcp_server.py"
      ],
      "env": {
        "PLANTOS_API_URL": "http://localhost:8000",
        "PLANTOS_API_KEY": "test-key-local-dev"
      }
    }
  }
}
```

### 6. Restart Claude Desktop

Quit Claude Desktop completely and restart.

## Try It Out

Open Claude Desktop and ask:

**Example 1: Farm Analysis**
```
"Analyze the farming potential at coordinates 41.8781, -87.6298"
```

**Example 2: Market Data**
```
"What are the current prices for corn, soybeans, and wheat?"
```

**Example 3: Agricultural Advice**
```
"What crops would be most profitable in Iowa right now?"
```

## Verify It's Working

Look for these indicators in Claude Desktop:
- Tools icon appears when chatting
- Claude mentions using "Plantos" tools
- You get detailed agricultural data in responses

## Common Issues

### Tools not showing up?
- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`
- Verify absolute paths in config
- Restart Claude Desktop completely

### Connection errors?
- Ensure Plantos API is running on port 8000
- Check `http://localhost:8000/docs` in browser
- Verify PLANTOS_API_URL in config

### Authentication errors?
- Check PLANTOS_API_KEY matches your API configuration
- Verify API key is active in database

## What's Next?

- Read [README.md](README.md) for complete documentation
- Explore all 7 available tools
- Check API documentation at `http://localhost:8000/docs`
- Try combining multiple tools in one conversation

## Need Help?

- API logs: Check farming-advisor-api terminal
- MCP logs: `~/Library/Logs/Claude/mcp*.log`
- Test API: `curl http://localhost:8000/api/v1/health`
