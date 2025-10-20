# Plantos MCP Server

Model Context Protocol (MCP) server that exposes the Plantos agricultural intelligence API as tools for Claude and other AI assistants.

## Overview

This MCP server wraps the Plantos API, allowing AI assistants to:
- Analyze farm locations for optimal crop selection
- Get real-time soil data from SSURGO database
- Fetch current weather data from NOAA
- Access live commodity market prices
- Chat with an agricultural advisor powered by RAG
- Generate economic analysis and farming recommendations

## Available Tools

### 1. `analyze_farm_location`
Comprehensive agricultural analysis for a specific location.

**Inputs:**
- `latitude` (number): Latitude coordinate (-90 to 90)
- `longitude` (number): Longitude coordinate (-180 to 180)

**Returns:**
- Soil properties and insights
- Weather conditions
- Crop yield predictions (87% accuracy)
- Live market data
- Economic analysis (revenue, costs, ROI)
- AI-generated recommendations

### 2. `get_soil_data`
Get detailed soil properties using SSURGO database.

**Inputs:**
- `latitude` (number): Latitude coordinate
- `longitude` (number): Longitude coordinate

**Returns:** Soil texture, drainage, pH, organic matter, composition

### 3. `get_weather_data`
Get current weather data from NOAA Weather.gov API.

**Inputs:**
- `latitude` (number): Latitude coordinate
- `longitude` (number): Longitude coordinate

**Returns:** Temperature, precipitation, humidity, growing degree days, wind data

### 4. `get_market_data`
Get live commodity market prices from USDA and CME.

**Inputs:**
- `crops` (string): Comma-separated crop types (e.g., "corn,soybeans,wheat")
- `latitude` (number, optional): For regional price adjustments
- `longitude` (number, optional): For regional price adjustments

**Returns:** Current prices, futures prices, price trends

### 5. `get_market_summary`
Get comprehensive market summary with location-based insights.

**Inputs:**
- `latitude` (number, optional): For regional context
- `longitude` (number, optional): For regional context

**Returns:** Market overview, trends, regional context

### 6. `chat_with_agricultural_advisor`
Ask questions to an AI agricultural advisor powered by RAG.

**Inputs:**
- `message` (string): Your question
- `context` (object, optional): Location, soil, weather, crop, and economic data

**Returns:** Evidence-based answer with source citations

### 7. `get_api_health`
Check API health status and database connection.

**Returns:** API status, database connectivity, timestamp

## Installation

### Prerequisites
- Python 3.10 or higher
- Running Plantos API instance
- API key for Plantos API

### Setup

1. **Install dependencies:**
```bash
cd mcp-server
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings:
# PLANTOS_API_URL=http://localhost:8000
# PLANTOS_API_KEY=your-api-key-here
```

3. **Test the server:**
```bash
python src/plantos_mcp_server.py
```

## Integration with Claude Desktop

Add this configuration to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "plantos": {
      "command": "python",
      "args": [
        "/absolute/path/to/plantos/mcp-server/src/plantos_mcp_server.py"
      ],
      "env": {
        "PLANTOS_API_URL": "http://localhost:8000",
        "PLANTOS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Replace `/absolute/path/to/plantos/` with the actual path to your installation.

### Restart Claude Desktop

After adding the configuration, restart Claude Desktop. You should see the Plantos tools available in the tools menu.

## Usage Examples

### Example 1: Analyze a Farm Location
```
Ask Claude: "Analyze the farming potential for coordinates 42.3601, -71.0589"

Claude will use the analyze_farm_location tool and provide:
- Soil analysis
- Weather conditions
- Crop recommendations with predicted yields
- Market prices
- Economic analysis showing expected profits
```

### Example 2: Get Market Insights
```
Ask Claude: "What are the current prices for corn and soybeans in Iowa?"

Claude will use get_market_data with location context to provide:
- Current spot prices
- Futures prices
- Price trends
- Regional adjustments
```

### Example 3: Chat with Agricultural Advisor
```
Ask Claude: "What are the best practices for improving soil health in sandy soils?"

Claude will use chat_with_agricultural_advisor to provide:
- Evidence-based recommendations
- Source citations from agricultural research
- Practical implementation steps
```

### Example 4: Complete Farm Planning
```
Ask Claude: "I'm at 41.8781, -87.6298 and want to maximize profit.
What crops should I plant and what's the expected return?"

Claude will:
1. Use analyze_farm_location to get comprehensive data
2. Use chat_with_agricultural_advisor for strategic advice
3. Synthesize results into actionable recommendations
```

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  Plantos MCP    │
│     Server      │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│  Plantos API    │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    │         │          │           │
┌───▼───┐ ┌──▼──┐  ┌────▼────┐ ┌───▼───┐
│ SSURGO│ │NOAA │  │  USDA   │ │  ML   │
│  Soil │ │ API │  │  MARS   │ │ Model │
└───────┘ └─────┘  └─────────┘ └───────┘
```

## Development

### Project Structure
```
mcp-server/
├── src/
│   └── plantos_mcp_server.py   # Main MCP server implementation
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── claude_desktop_config.json   # Claude Desktop config example
└── README.md                    # This file
```

### Testing

1. **Start your Plantos API:**
```bash
cd farming-advisor-api
python run.py
```

2. **Run the MCP server:**
```bash
cd mcp-server
python src/plantos_mcp_server.py
```

3. **Test in Claude Desktop:**
   - Add configuration to claude_desktop_config.json
   - Restart Claude Desktop
   - Try asking Claude to use Plantos tools

### Debugging

Enable debug logging:
```bash
export MCP_DEBUG=1
python src/plantos_mcp_server.py
```

Check Claude Desktop logs:
- **macOS:** `~/Library/Logs/Claude/mcp*.log`
- **Windows:** `%APPDATA%\Claude\Logs\mcp*.log`

## Security

- Store API keys securely in environment variables
- Use HTTPS for production API endpoints
- Implement rate limiting on the API side
- Never commit .env files to version control

## Troubleshooting

### "Connection refused" errors
- Ensure Plantos API is running on the configured URL
- Check PLANTOS_API_URL in your configuration
- Verify firewall settings

### "Authentication failed" errors
- Verify PLANTOS_API_KEY is correct
- Check API key is active in Plantos database
- Ensure API key has proper permissions

### Tools not appearing in Claude Desktop
- Verify claude_desktop_config.json syntax
- Check file paths are absolute, not relative
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors

### "No data available" responses
- Verify location coordinates are valid
- Check Plantos API has data for that region
- Try a different location (e.g., Iowa farmland)

## Performance

- Tool calls typically complete in 2-5 seconds
- Weather data cached by NOAA API
- Market data updates every 15 minutes
- Concurrent tool calls supported

## Limitations

- Weather data only available for US locations (NOAA restriction)
- Soil data coverage limited to SSURGO database areas
- Market data may have slight delays (~15 minutes)
- RAG chat requires OpenAI API key or configured LLM

## Future Enhancements

- [ ] Add real-time weather alerts
- [ ] Support international locations
- [ ] Add field boundary analysis
- [ ] Implement crop rotation planning
- [ ] Add pest and disease prediction
- [ ] Support multi-year planning
- [ ] Add irrigation optimization

## Support

For issues or questions:
- API Issues: Check farming-advisor-api logs
- MCP Issues: Check Claude Desktop logs
- Documentation: See Plantos main README

## License

Same license as Plantos project.

## Credits

Built on:
- [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
- [Plantos API](../farming-advisor-api/README.md)
- SSURGO soil database (USDA NRCS)
- NOAA Weather.gov API
- USDA MARS commodity data
