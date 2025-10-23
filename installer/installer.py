#!/usr/bin/env python3
"""
Plantos MCP Installer
Automatically configures Claude Desktop and ChatGPT to use Plantos MCP server
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import sys
from pathlib import Path
from threading import Thread
from PIL import Image, ImageTk

from auth import authenticate_user
from config_editor import detect_configs, update_config, install_mcp_server


class PlantosInstaller(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Plantos MCP Setup")
        self.geometry("500x750")
        self.resizable(False, False)

        # State
        self.api_key = None
        self.user_email = None
        self.auth_code = None

        # Style
        self.configure(bg="#f5f5f5")

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg="#16a34a", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Load and display Sprout icon with title
        try:
            # Get path to icon file (works both from source and PyInstaller bundle)
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent

            # Use high-resolution source and downsample for better quality
            icon_path = base_path / "sprout_icon_128.png"  # Use high-res 128px icon
            icon_image = Image.open(icon_path)

            # Add white circular background for contrast against green header
            # Draw at 4x resolution for smooth anti-aliased edges, then downsample
            from PIL import ImageDraw
            final_size = 50  # Final display size
            scale = 4  # Draw at 4x resolution for anti-aliasing
            hi_res_size = final_size * scale  # 200px
            circle_size = 46 * scale  # 184px
            padding = (hi_res_size - circle_size) // 2

            # Create high-resolution background with white circle
            background = Image.new('RGBA', (hi_res_size, hi_res_size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(background)
            # Draw white circle well within bounds
            draw.ellipse([padding, padding, padding + circle_size - 1, padding + circle_size - 1],
                        fill='white', outline='white')

            # Paste the 128px icon centered in the circle (will be 32px when downsampled)
            icon_offset = (hi_res_size - 128) // 2
            background.paste(icon_image, (icon_offset, icon_offset), icon_image if icon_image.mode == 'RGBA' else None)

            # Downsample to final size with high-quality Lanczos filter for smooth edges
            background = background.resize((final_size, final_size), Image.Resampling.LANCZOS)

            icon_photo = ImageTk.PhotoImage(background)

            # Container for icon and text
            title_container = tk.Frame(header_frame, bg="#16a34a")
            title_container.pack(pady=25)

            # Icon with white background - use Canvas for better control
            from tkinter import Canvas
            icon_canvas = Canvas(
                title_container,
                width=final_size,
                height=final_size,
                bg="#16a34a",
                highlightthickness=0,
                relief='flat'
            )
            icon_canvas.create_image(final_size//2, final_size//2, image=icon_photo)
            icon_canvas.image = icon_photo  # Keep a reference to prevent garbage collection
            icon_canvas.pack(side=tk.LEFT, padx=(0, 10))

            # Title text
            title_label = tk.Label(
                title_container,
                text="Plantos MCP",
                font=("Arial", 24, "bold"),
                bg="#16a34a",
                fg="white"
            )
            title_label.pack(side=tk.LEFT)

        except Exception as e:
            # Fallback if icon can't be loaded
            print(f"Could not load icon: {e}")
            title_label = tk.Label(
                header_frame,
                text="Plantos MCP",
                font=("Arial", 24, "bold"),
                bg="#16a34a",
                fg="white"
            )
            title_label.pack(pady=30)

        # Main content
        content_frame = tk.Frame(self, bg="#f5f5f5", padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Welcome text
        welcome_text = tk.Label(
            content_frame,
            text="Connect Claude Desktop to Plantos\nAgricultural Intelligence",
            font=("Arial", 14),
            bg="#f5f5f5",
            fg="#333",
            justify=tk.CENTER
        )
        welcome_text.pack(pady=(0, 20))

        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="Ready to configure your AI assistant",
            font=("Arial", 10),
            bg="#f5f5f5",
            fg="#666"
        )
        self.status_label.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            content_frame,
            length=400,
            mode='determinate'
        )
        self.progress.pack(pady=10)

        # Detected AI assistants
        self.detected_frame = tk.LabelFrame(
            content_frame,
            text="Detected AI Assistants",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#333",  # Dark gray text for visibility
            padx=15,
            pady=15
        )
        self.detected_frame.pack(pady=20, fill=tk.X)

        self.detected_label = tk.Label(
            self.detected_frame,
            text="Scanning...",
            font=("Arial", 10),
            bg="#f5f5f5",
            fg="#666",
            justify=tk.LEFT
        )
        self.detected_label.pack(anchor=tk.W)

        # Sign in button
        self.signin_button = tk.Button(
            content_frame,
            text="Sign In to Plantos",
            command=self.start_signin,
            font=("Arial", 12, "bold"),
            bg="#16a34a",
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2"
        )
        self.signin_button.pack(pady=20)

        # Footer
        footer_text = tk.Label(
            content_frame,
            text="Need help? Visit plantos.co/support",
            font=("Arial", 9),
            bg="#f5f5f5",
            fg="#999",
            cursor="hand2"
        )
        footer_text.pack(side=tk.BOTTOM, pady=10)
        footer_text.bind("<Button-1>", lambda e: webbrowser.open("https://plantos.co/support"))

        # Detect configs on startup
        self.after(500, self.scan_configs)

    def scan_configs(self):
        """Scan for Claude and ChatGPT installations"""
        self.update_status("Scanning for AI assistants...")
        self.progress['value'] = 20

        configs = detect_configs()

        if not configs:
            self.detected_label.config(
                text="❌ No AI assistants found\n\nPlease install Claude Desktop or ChatGPT first.",
                fg="#dc2626"
            )
            self.signin_button.config(state=tk.DISABLED)
            self.progress['value'] = 0
            return

        # Show detected assistants
        detected_text = ""
        for config in configs:
            detected_text += f"✓ {config['name']} ({config['type']})\n"
            detected_text += f"  {config['path']}\n\n"

        self.detected_label.config(text=detected_text.strip(), fg="#16a34a")
        self.progress['value'] = 40
        self.update_status("Ready to sign in")

    def start_signin(self):
        """Start authentication flow"""
        self.update_status("Opening browser for sign in...")
        self.progress['value'] = 50
        self.signin_button.config(state=tk.DISABLED)

        # Run authentication in background thread to prevent UI freeze
        auth_thread = Thread(target=self.authenticate_in_background, daemon=True)
        auth_thread.start()

    def authenticate_in_background(self):
        """Run authentication in background thread"""
        try:
            result = authenticate_user()

            # Update UI from main thread
            self.after(0, lambda: self.handle_auth_result(result))

        except Exception as e:
            self.after(0, lambda: self.handle_auth_error(e))

    def handle_auth_result(self, result):
        """Handle authentication result in main thread"""
        if result:
            self.api_key = result['api_key']
            self.user_email = result.get('email', 'user@plantos.co')
            self.auth_code = result.get('code', 'N/A')
            self.progress['value'] = 70
            self.update_status(f"Signed in successfully!")
            self.configure_assistants()
        else:
            self.update_status("Sign in cancelled")
            self.signin_button.config(state=tk.NORMAL)
            self.progress['value'] = 40

    def handle_auth_error(self, error):
        """Handle authentication error in main thread"""
        messagebox.showerror(
            "Authentication Error",
            f"Failed to sign in:\n{str(error)}\n\nPlease try again or visit plantos.co/support"
        )
        self.signin_button.config(state=tk.NORMAL)
        self.progress['value'] = 40
        self.update_status("Sign in failed")

    def configure_assistants(self):
        """Configure detected AI assistants"""
        self.update_status("Installing MCP server...")
        self.progress['value'] = 75

        try:
            # Get path to bundled MCP server source
            # When running from source, look in parent directory
            # When running as executable, PyInstaller bundles it
            if getattr(sys, 'frozen', False):
                # Running as executable
                base_path = Path(sys._MEIPASS)
                mcp_source = base_path / "src"
            else:
                # Running from source (installer/ directory)
                base_path = Path(__file__).parent.parent
                mcp_source = base_path / "src"

            # Install MCP server locally
            server_path = install_mcp_server(mcp_source)
            self.update_status("Configuring AI assistants...")
            self.progress['value'] = 85

        except Exception as e:
            messagebox.showerror(
                "Installation Error",
                f"Failed to install MCP server:\n{str(e)}\n\nPlease try again or contact support."
            )
            self.update_status("Installation failed")
            self.signin_button.config(state=tk.NORMAL)
            self.progress['value'] = 40
            return

        configs = detect_configs()
        configured_count = 0

        for config in configs:
            try:
                success = update_config(
                    config_path=config['path'],
                    api_key=self.api_key,
                    mcp_server_path=server_path
                )

                if success:
                    configured_count += 1
            except Exception as e:
                print(f"Failed to configure {config['name']}: {e}")

        self.progress['value'] = 100

        if configured_count > 0:
            self.show_success(configured_count)
        else:
            messagebox.showerror(
                "Configuration Failed",
                "Failed to configure any AI assistants.\n\nPlease try manual setup at plantos.co/mcp/download"
            )
            self.update_status("Configuration failed")

    def show_success(self, count):
        """Show success message"""
        self.update_status("Configuration complete!")

        # Make window taller and resizable for success screen
        self.geometry("500x850")
        self.resizable(True, True)

        # Hide signin button, show success message
        self.signin_button.pack_forget()

        success_frame = tk.Frame(self.detected_frame.master, bg="#f5f5f5")
        success_frame.pack(pady=20)

        success_icon = tk.Label(
            success_frame,
            text="✅",
            font=("Arial", 48),
            bg="#f5f5f5"
        )
        success_icon.pack()

        success_text = tk.Label(
            success_frame,
            text=f"Installation Complete!",
            font=("Arial", 16, "bold"),
            bg="#f5f5f5",
            fg="#16a34a"
        )
        success_text.pack(pady=5)

        subtitle = tk.Label(
            success_frame,
            text=f"Successfully configured {count} AI assistant(s)",
            font=("Arial", 11),
            bg="#f5f5f5",
            fg="#666"
        )
        subtitle.pack(pady=(0, 10))

        # Authorization code display
        if self.auth_code:
            code_box = tk.Frame(success_frame, bg="white", relief=tk.SOLID, bd=1)
            code_box.pack(pady=(0, 15), padx=20, fill=tk.X)

            code_label = tk.Label(
                code_box,
                text="Authorization Code:",
                font=("Arial", 9, "bold"),
                bg="white",
                fg="#666"
            )
            code_label.pack(pady=(8, 2), padx=10, anchor=tk.W)

            code_value = tk.Label(
                code_box,
                text=self.auth_code,
                font=("Courier", 14, "bold"),
                bg="white",
                fg="#16a34a"
            )
            code_value.pack(pady=(0, 8), padx=10)

        # Instructions box with more padding
        instructions_box = tk.Frame(success_frame, bg="#dcfce7", relief=tk.FLAT, bd=0)
        instructions_box.pack(pady=15, padx=20, fill=tk.X)

        instructions_title = tk.Label(
            instructions_box,
            text="IMPORTANT: Next Steps",
            font=("Arial", 10, "bold"),
            bg="#dcfce7",
            fg="#166534"
        )
        instructions_title.pack(pady=(15, 10))

        instructions = tk.Label(
            instructions_box,
            text="1. CLOSE this installer window\n\n"
                 "2. RESTART Claude Desktop\n"
                 "   (Quit completely and reopen - don't just refresh)\n\n"
                 "3. TEST by asking Claude:\n"
                 '   "What\'s the weather in Iowa?"\n\n'
                 "4. Plantos tools are now available!",
            font=("Arial", 9),
            bg="#dcfce7",
            fg="#166534",
            justify=tk.LEFT
        )
        instructions.pack(pady=(0, 15), padx=15)

        # Close button
        close_button = tk.Button(
            success_frame,
            text="Close Installer",
            command=self.quit,
            font=("Arial", 12, "bold"),
            bg="#16a34a",
            fg="white",
            relief=tk.FLAT,
            padx=50,
            pady=12,
            cursor="hand2",
            activebackground="#15803d",
            activeforeground="white"
        )
        close_button.pack(pady=20)

    def update_status(self, text):
        """Update status label"""
        self.status_label.config(text=text)
        self.update()


def main():
    """Run the installer"""
    app = PlantosInstaller()
    app.mainloop()


if __name__ == "__main__":
    main()
