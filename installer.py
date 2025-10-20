#!/usr/bin/env python3
"""
Plantos MCP Desktop Installer
OAuth-style authorization flow for easy MCP setup
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import platform
import sys
import time
import threading
import webbrowser
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Installing required package: requests")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# API Configuration
API_BASE_URL = "https://api.plantos.co"
VERIFICATION_URL = "https://plantos.co"

# SSL Certificate configuration
# Use system CA bundle instead of certifi for better compatibility
def get_ca_bundle():
    """Get the appropriate CA bundle for SSL verification"""
    import os

    # Try system locations
    system_certs = [
        '/etc/ssl/cert.pem',  # macOS/BSD
        '/etc/ssl/certs/ca-certificates.crt',  # Debian/Ubuntu/Gentoo
        '/etc/pki/tls/certs/ca-bundle.crt',  # Fedora/RHEL
       '/etc/ssl/ca-bundle.pem',  # OpenSUSE
    ]

    for cert_path in system_certs:
        if os.path.exists(cert_path):
            return cert_path

    # Fall back to requests default (uses certifi)
    return True

class PlantosInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Plantos MCP Desktop Installer")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # State
        self.auth_code: Optional[str] = None
        self.api_key: Optional[str] = None
        self.polling: bool = False

        # Style
        self.setup_styles()

        # UI
        self.create_widgets()

    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Colors
        self.bg_color = "#f9fafb"
        self.primary_color = "#16a34a"  # green-600
        self.text_color = "#111827"
        self.secondary_text = "#6b7280"

        # Configure styles
        style.configure('Title.TLabel',
                       font=('Helvetica', 24, 'bold'),
                       foreground=self.text_color)
        style.configure('Header.TLabel',
                       font=('Helvetica', 16, 'bold'),
                       foreground=self.text_color)
        style.configure('Body.TLabel',
                       font=('Helvetica', 11),
                       foreground=self.secondary_text)
        style.configure('Code.TLabel',
                       font=('Courier', 32, 'bold'),
                       foreground=self.primary_color)
        style.configure('Primary.TButton',
                       font=('Helvetica', 12, 'bold'),
                       background=self.primary_color)

    def create_widgets(self):
        """Create UI elements"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo/Title
        title = ttk.Label(main_frame,
                         text="🌾 Plantos MCP",
                         style='Title.TLabel')
        title.pack(pady=(0, 10))

        subtitle = ttk.Label(main_frame,
                           text="Agricultural Intelligence for Claude Desktop",
                           style='Body.TLabel')
        subtitle.pack(pady=(0, 30))

        # Content frame (changes based on state)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Show initial screen
        self.show_welcome_screen()

    def show_welcome_screen(self):
        """Show welcome screen with install button"""
        self.clear_content()

        welcome_text = ttk.Label(self.content_frame,
                                text="Connect your Plantos account to Claude Desktop\n\n" +
                                     "This installer will:\n" +
                                     "• Open your browser to authorize the connection\n" +
                                     "• Automatically configure Claude Desktop\n" +
                                     "• Enable Plantos tools in your AI workflow",
                                style='Body.TLabel',
                                justify=tk.CENTER)
        welcome_text.pack(pady=40)

        install_btn = ttk.Button(self.content_frame,
                                text="Install Plantos MCP",
                                style='Primary.TButton',
                                command=self.start_installation)
        install_btn.pack(pady=10, ipadx=40, ipady=15)

    def show_authorization_screen(self):
        """Show authorization code and instructions"""
        self.clear_content()

        header = ttk.Label(self.content_frame,
                          text="Authorization Required",
                          style='Header.TLabel')
        header.pack(pady=(20, 10))

        instructions = ttk.Label(self.content_frame,
                                text="Your browser will open to authorize this connection.\n" +
                                     "If it doesn't open automatically, visit:",
                                style='Body.TLabel',
                                justify=tk.CENTER)
        instructions.pack(pady=10)

        # URL link
        url_label = ttk.Label(self.content_frame,
                             text=f"{VERIFICATION_URL}/mcp/authorize",
                             style='Body.TLabel',
                             foreground=self.primary_color,
                             cursor="hand2")
        url_label.pack(pady=5)
        url_label.bind("<Button-1>", lambda e: webbrowser.open(f"{VERIFICATION_URL}/mcp/authorize?code={self.auth_code}"))

        # Authorization code
        code_frame = ttk.Frame(self.content_frame)
        code_frame.pack(pady=30)

        code_label = ttk.Label(code_frame,
                              text="Your Code:",
                              style='Body.TLabel')
        code_label.pack()

        code_display = ttk.Label(code_frame,
                                text=self.auth_code or "----",
                                style='Code.TLabel')
        code_display.pack(pady=10)

        # Status
        self.status_label = ttk.Label(self.content_frame,
                                     text="Waiting for authorization...",
                                     style='Body.TLabel')
        self.status_label.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(self.content_frame,
                                       mode='indeterminate',
                                       length=300)
        self.progress.pack(pady=10)
        self.progress.start()

    def show_success_screen(self):
        """Show success message"""
        self.clear_content()

        success_icon = ttk.Label(self.content_frame,
                                text="✅",
                                font=('Helvetica', 72))
        success_icon.pack(pady=30)

        header = ttk.Label(self.content_frame,
                          text="Installation Complete!",
                          style='Header.TLabel')
        header.pack(pady=10)

        message = ttk.Label(self.content_frame,
                           text="Plantos MCP has been configured in Claude Desktop.\n\n" +
                                "Restart Claude Desktop to start using Plantos tools.",
                           style='Body.TLabel',
                           justify=tk.CENTER)
        message.pack(pady=20)

        close_btn = ttk.Button(self.content_frame,
                              text="Close",
                              style='Primary.TButton',
                              command=self.root.quit)
        close_btn.pack(pady=20, ipadx=40, ipady=15)

    def show_error_screen(self, error_message: str):
        """Show error message"""
        self.clear_content()

        error_icon = ttk.Label(self.content_frame,
                              text="❌",
                              font=('Helvetica', 72))
        error_icon.pack(pady=30)

        header = ttk.Label(self.content_frame,
                          text="Installation Failed",
                          style='Header.TLabel')
        header.pack(pady=10)

        message = ttk.Label(self.content_frame,
                           text=error_message,
                           style='Body.TLabel',
                           justify=tk.CENTER,
                           wraplength=500)
        message.pack(pady=20)

        retry_btn = ttk.Button(self.content_frame,
                              text="Try Again",
                              style='Primary.TButton',
                              command=self.show_welcome_screen)
        retry_btn.pack(pady=10, ipadx=40, ipady=15)

    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def start_installation(self):
        """Start the OAuth flow"""
        threading.Thread(target=self._installation_thread, daemon=True).start()

    def _installation_thread(self):
        """Installation process in background thread"""
        try:
            # Step 1: Request authorization code
            self.root.after(0, self.update_status, "Requesting authorization code...")
            code_data = self.request_authorization_code()

            if not code_data:
                raise Exception("Failed to get authorization code from server")

            self.auth_code = code_data['code']
            verification_url = code_data['verification_url']

            # Step 2: Show authorization screen and open browser
            self.root.after(0, self.show_authorization_screen)
            time.sleep(1)
            webbrowser.open(verification_url)

            # Step 3: Poll for authorization
            self.polling = True
            self.api_key = self.poll_for_authorization()

            if not self.api_key:
                raise Exception("Authorization timeout or failed. Please try again.")

            # Step 4: Configure Claude Desktop
            self.root.after(0, self.update_status, "Configuring Claude Desktop...")
            self.configure_claude_desktop()

            # Step 5: Success!
            self.root.after(0, self.show_success_screen)

        except Exception as e:
            self.root.after(0, self.show_error_screen, str(e))

    def request_authorization_code(self) -> Optional[dict]:
        """Request authorization code from API"""
        try:
            url = f"{API_BASE_URL}/api/v1/mcp/request-code"
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                timeout=10,
                verify=get_ca_bundle()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error requesting code: {e}")
            return None

    def poll_for_authorization(self, timeout: int = 300) -> Optional[str]:
        """Poll API until code is authorized"""
        start_time = time.time()

        while self.polling and (time.time() - start_time) < timeout:
            try:
                url = f"{API_BASE_URL}/api/v1/mcp/check-code?code={self.auth_code}"
                response = requests.get(url, timeout=10, verify=get_ca_bundle())

                if response.status_code == 404:
                    raise Exception("Invalid authorization code")

                response.raise_for_status()
                data = response.json()

                if data['status'] == 'authorized':
                    return data['api_key']
                elif data['status'] == 'expired':
                    raise Exception("Authorization code expired")

            except requests.exceptions.RequestException as e:
                print(f"Polling error: {e}")

            time.sleep(3)  # Poll every 3 seconds

        return None

    def configure_claude_desktop(self):
        """Configure Claude Desktop with MCP server"""
        config_path = self.get_claude_config_path()

        if not config_path:
            raise Exception("Could not find Claude Desktop configuration directory")

        # Load existing config or create new
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {"mcpServers": {}}

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Get MCP server script path
        server_path = Path(__file__).parent / "src" / "plantos_mcp_server.py"

        # Add Plantos MCP server
        config["mcpServers"]["plantos"] = {
            "command": sys.executable,
            "args": [str(server_path)],
            "env": {
                "PLANTOS_API_URL": API_BASE_URL,
                "PLANTOS_API_KEY": self.api_key
            }
        }

        # Write config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def get_claude_config_path(self) -> Optional[Path]:
        """Get Claude Desktop config path for current OS"""
        system = platform.system()

        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif system == "Windows":
            return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        elif system == "Linux":
            return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
        else:
            return None

    def update_status(self, message: str):
        """Update status label"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PlantosInstaller(root)
    root.mainloop()


if __name__ == "__main__":
    main()
