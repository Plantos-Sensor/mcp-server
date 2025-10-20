#!/bin/bash
# Plantos MCP Server Setup Script

set -e

echo "=================================="
echo "Plantos MCP Server Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env with your Plantos API settings:"
    echo "   - PLANTOS_API_URL"
    echo "   - PLANTOS_API_KEY"
fi

# Display next steps
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API settings:"
echo "   nano .env"
echo ""
echo "2. Start your Plantos API (in another terminal):"
echo "   cd ../farming-advisor-api"
echo "   python run.py"
echo ""
echo "3. Test the MCP server:"
echo "   python src/plantos_mcp_server.py"
echo ""
echo "4. To use with Claude Desktop, add this to your config:"
echo "   ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "   See README.md for full configuration details"
echo ""
