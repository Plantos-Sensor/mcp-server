#!/bin/bash
# Plantos MCP Installer
# One-click installer for connecting Plantos to Claude Desktop

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# API endpoint
API_URL="${PLANTOS_API_URL:-https://api.plantos.co}"

echo ""
echo "🌾 Plantos MCP Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}✓${NC} Python $PYTHON_VERSION found"

# Check if pip is installed
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip is not installed${NC}"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade || {
        echo "Failed to install pip. Please install it manually."
        read -p "Press Enter to exit..."
        exit 1
    }
fi

echo -e "${BLUE}✓${NC} pip found"
echo ""

# Step 1: Request authorization code
echo -e "${BLUE}Requesting authorization code...${NC}"
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/mcp/request-code" \
    -H "Content-Type: application/json") || {
    echo -e "${RED}❌ Failed to connect to Plantos API${NC}"
    echo "Please check your internet connection and try again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
}

# Parse the response
CODE=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('code', ''))" 2>/dev/null || echo "")
VERIFICATION_URL=$(echo "$AUTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('verification_url', ''))" 2>/dev/null || echo "")

if [ -z "$CODE" ]; then
    echo -e "${RED}❌ Failed to get authorization code${NC}"
    echo "Response: $AUTH_RESPONSE"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}📱 Your authorization code:${NC}"
echo ""
echo -e "         ${YELLOW}$CODE${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Opening your browser to authorize..."
echo "If the browser doesn't open, visit:"
echo "$VERIFICATION_URL"
echo ""

# Open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$VERIFICATION_URL" 2>/dev/null || true
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$VERIFICATION_URL" 2>/dev/null || true
fi

# Step 2: Poll for authorization
echo -e "${BLUE}Waiting for authorization...${NC}"
echo "(This will time out in 5 minutes if not authorized)"
echo ""

MAX_ATTEMPTS=60  # 5 minutes (5 second intervals)
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))

    CHECK_RESPONSE=$(curl -s "$API_URL/api/v1/mcp/check-code?code=$CODE") || continue

    STATUS=$(echo "$CHECK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "")

    if [ "$STATUS" = "authorized" ]; then
        API_KEY=$(echo "$CHECK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('api_key', ''))" 2>/dev/null || echo "")

        if [ -n "$API_KEY" ]; then
            echo -e "${GREEN}✓ Authorization successful!${NC}"
            echo ""
            break
        fi
    elif [ "$STATUS" = "expired" ]; then
        echo -e "${RED}❌ Authorization code expired${NC}"
        echo "Please run the installer again."
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi

    # Show progress
    if [ $((ATTEMPT % 6)) -eq 0 ]; then
        echo -e "${BLUE}Still waiting... ($((ATTEMPT * 5))s elapsed)${NC}"
    fi
done

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ Authorization timed out${NC}"
    echo "Please run the installer again and authorize within 5 minutes."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Step 3: Install plantos-mcp
echo -e "${BLUE}Installing Plantos MCP server...${NC}"
python3 -m pip install --upgrade plantos-mcp --quiet || {
    echo -e "${RED}❌ Failed to install plantos-mcp${NC}"
    echo "Please check your Python installation and try again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
}

echo -e "${GREEN}✓ Plantos MCP installed${NC}"
echo ""

# Step 4: Configure Claude Desktop
echo -e "${BLUE}Configuring Claude Desktop...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_DIR="$HOME/.config/Claude"
else
    echo -e "${RED}❌ Unsupported operating system${NC}"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Read existing config or create new one
if [ -f "$CONFIG_FILE" ]; then
    EXISTING_CONFIG=$(cat "$CONFIG_FILE")
else
    EXISTING_CONFIG='{}'
fi

# Add Plantos MCP to config
NEW_CONFIG=$(echo "$EXISTING_CONFIG" | python3 -c "
import sys, json

config = json.load(sys.stdin)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['plantos'] = {
    'command': 'plantos-mcp',
    'env': {
        'PLANTOS_API_KEY': '$API_KEY'
    }
}

print(json.dumps(config, indent=2))
")

echo "$NEW_CONFIG" > "$CONFIG_FILE"

echo -e "${GREEN}✓ Claude Desktop configured${NC}"
echo ""

# Success!
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop (if it's running)"
echo "2. Start a new conversation"
echo "3. Ask Claude about weather, soil, crops, etc."
echo ""
echo "Example prompts:"
echo '  • "What'\''s the weather like for farming in Austin, TX?"'
echo '  • "Analyze the soil at coordinates 30.2672, -97.7431"'
echo '  • "Predict corn yield for my location"'
echo ""
echo "Need help? Visit https://plantos.co/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Press Enter to close..."
