"""
Config file editor for Claude Desktop and ChatGPT
Detects installation locations and updates MCP configuration
"""

import json
import platform
import os
import shutil
import subprocess
from pathlib import Path


def detect_configs():
    """
    Detect installed AI assistants and their config file locations
    Returns: list of dicts with 'name', 'type', 'path'
    """
    system = platform.system()
    configs = []

    if system == "Darwin":  # macOS
        # Claude Desktop
        claude_config = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        if claude_config.parent.exists():
            configs.append({
                "name": "Claude Desktop",
                "type": "claude",
                "path": str(claude_config)
            })

        # ChatGPT (if exists - path may vary)
        chatgpt_config = Path.home() / ".config/chatgpt/config.json"
        if chatgpt_config.parent.exists():
            configs.append({
                "name": "ChatGPT Desktop",
                "type": "chatgpt",
                "path": str(chatgpt_config)
            })

    elif system == "Windows":
        # Claude Desktop on Windows
        appdata = os.getenv("APPDATA")
        if appdata:
            claude_config = Path(appdata) / "Claude/claude_desktop_config.json"
            if claude_config.parent.exists():
                configs.append({
                    "name": "Claude Desktop",
                    "type": "claude",
                    "path": str(claude_config)
                })

            # ChatGPT on Windows
            chatgpt_config = Path(appdata) / "ChatGPT/config.json"
            if chatgpt_config.parent.exists():
                configs.append({
                    "name": "ChatGPT Desktop",
                    "type": "chatgpt",
                    "path": str(chatgpt_config)
                })

    elif system == "Linux":
        # Claude Desktop on Linux
        claude_config = Path.home() / ".config/Claude/claude_desktop_config.json"
        if claude_config.parent.exists():
            configs.append({
                "name": "Claude Desktop",
                "type": "claude",
                "path": str(claude_config)
            })

        # ChatGPT on Linux
        chatgpt_config = Path.home() / ".config/chatgpt/config.json"
        if chatgpt_config.parent.exists():
            configs.append({
                "name": "ChatGPT Desktop",
                "type": "chatgpt",
                "path": str(chatgpt_config)
            })

    return configs


def get_mcp_install_dir():
    """
    Get the directory where MCP server should be installed
    Returns: Path to MCP installation directory
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        install_dir = Path.home() / "Library/Application Support/Plantos/mcp-server"
    elif system == "Windows":
        appdata = os.getenv("APPDATA")
        install_dir = Path(appdata) / "Plantos/mcp-server" if appdata else Path.home() / "Plantos/mcp-server"
    else:  # Linux
        install_dir = Path.home() / ".config/Plantos/mcp-server"

    return install_dir


def install_mcp_server(source_dir):
    """
    Install MCP server files to local directory
    Args:
        source_dir: Directory containing MCP server source files
    Returns: Path to installed server.py
    """
    install_dir = get_mcp_install_dir()

    # Create install directory
    install_dir.mkdir(parents=True, exist_ok=True)

    # Copy MCP server files
    source_path = Path(source_dir)
    if not source_path.exists():
        raise FileNotFoundError(f"MCP server source not found: {source_dir}")

    # Copy all Python files and requirements.txt
    for item in source_path.rglob("*"):
        if item.is_file() and (item.suffix == ".py" or item.name == "requirements.txt"):
            relative_path = item.relative_to(source_path)
            dest_path = install_dir / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)

    # Install dependencies
    requirements_file = install_dir / "requirements.txt"
    if requirements_file.exists():
        try:
            subprocess.check_call([
                "python3", "-m", "pip", "install", "-q", "-r", str(requirements_file)
            ])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install dependencies: {e}")

    # Return path to server entry point
    server_path = install_dir / "src/plantos_mcp/server.py"
    if not server_path.exists():
        # Fallback: try to find server.py
        server_files = list(install_dir.rglob("server.py"))
        if server_files:
            server_path = server_files[0]
        else:
            raise FileNotFoundError("Could not find server.py in installed MCP server")

    return server_path


def update_config(config_path, api_key, mcp_server_path):
    """
    Update AI assistant config with Plantos MCP settings
    Args:
        config_path: Path to config file
        api_key: User's Plantos API key
        mcp_server_path: Path to locally installed MCP server
    Returns: True if successful
    """
    config_path = Path(config_path)

    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            # Invalid JSON, start fresh
            config = {}
    else:
        config = {}

    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add Plantos MCP configuration for stdio (local) mode
    config["mcpServers"]["plantos"] = {
        "command": "python3",
        "args": [str(mcp_server_path)],
        "env": {
            "PLANTOS_API_KEY": api_key,
            "PLANTOS_API_URL": "https://api.plantos.co"
        }
    }

    # Write config back
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False


def remove_plantos_config(config_path):
    """
    Remove Plantos MCP from config file
    Args:
        config_path: Path to config file
    Returns: True if successful
    """
    config_path = Path(config_path)

    if not config_path.exists():
        return True

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Remove plantos from mcpServers
        if "mcpServers" in config and "plantos" in config["mcpServers"]:
            del config["mcpServers"]["plantos"]

            # If mcpServers is now empty, remove it
            if not config["mcpServers"]:
                del config["mcpServers"]

        # Write back
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        return True
    except Exception as e:
        print(f"Error removing config: {e}")
        return False


def verify_config(config_path):
    """
    Verify that Plantos MCP is properly configured
    Args:
        config_path: Path to config file
    Returns: True if configured correctly
    """
    config_path = Path(config_path)

    if not config_path.exists():
        return False

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Check if plantos is configured
        if "mcpServers" not in config:
            return False

        if "plantos" not in config["mcpServers"]:
            return False

        plantos_config = config["mcpServers"]["plantos"]

        # Verify required fields
        if "url" not in plantos_config:
            return False

        if "transport" not in plantos_config:
            return False

        transport = plantos_config["transport"]
        if transport.get("type") != "http":
            return False

        if "headers" not in transport or "X-API-Key" not in transport["headers"]:
            return False

        return True

    except Exception:
        return False


if __name__ == "__main__":
    # Test config detection
    print("Detecting AI assistant installations...")
    configs = detect_configs()

    if not configs:
        print("❌ No AI assistants found")
    else:
        print(f"✓ Found {len(configs)} AI assistant(s):")
        for config in configs:
            print(f"  - {config['name']}: {config['path']}")
            exists = "✓ exists" if Path(config['path']).exists() else "✗ not found"
            print(f"    Config file: {exists}")
