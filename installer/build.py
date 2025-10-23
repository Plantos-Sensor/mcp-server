#!/usr/bin/env python3
"""
Build script for Plantos MCP Installer
Creates standalone executable for Mac, Windows, and Linux with code signing
"""

import PyInstaller.__main__
import platform
import subprocess
import sys
import os
from pathlib import Path

def build_installer(sign=False, identity=None):
    """Build installer executable using PyInstaller

    Args:
        sign: Whether to sign the executable (macOS only)
        identity: Code signing identity (e.g., "Developer ID Application: Your Name")
    """

    system = platform.system()

    # Common PyInstaller options
    options = [
        'installer.py',
        '--name=PlantosMCPInstaller',
        '--onefile',
        '--windowed',  # No console window
        # TODO: Add icon file with '--icon=path/to/icon.icns'
        '--add-data=auth.py:.',
        '--add-data=config_editor.py:.',
        '--add-data=../src:src',  # Bundle MCP server source
        '--hidden-import=mcp',
        '--hidden-import=httpx',
        '--hidden-import=pydantic',
        '--clean',
    ]

    # Platform-specific options
    if system == "Darwin":  # macOS
        options.extend([
            '--osx-bundle-identifier=co.plantos.mcp-installer',
            # Note: universal2 requires universal2 Python. Build for current arch only.
            # GitHub Actions will build universal2 using appropriate Python.
        ])

        # Add code signing options if requested
        if sign and identity:
            options.extend([
                f'--codesign-identity={identity}',
                '--osx-entitlements-file=entitlements.plist',
            ])

    elif system == "Windows":
        options.extend([
            '--version-file=version.txt',  # TODO: Create version file
        ])

    print(f"Building installer for {system}...")
    print("This may take a few minutes...")

    try:
        PyInstaller.__main__.run(options)
        print("\n✓ Build successful!")

        # Post-build: Sign and notarize on macOS
        if system == "Darwin" and sign:
            app_path = Path("dist/PlantosMCPInstaller.app")
            if app_path.exists():
                print("\nSigning macOS app...")
                sign_macos_app(app_path, identity)

                # Optionally notarize for distribution
                if os.getenv("NOTARIZE"):
                    print("\nNotarizing app...")
                    notarize_macos_app(app_path)

        print(f"\n✓ Executable location: dist/PlantosMCPInstaller")

    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        sys.exit(1)


def sign_macos_app(app_path: Path, identity: str):
    """Sign macOS app bundle with Apple Developer ID

    Args:
        app_path: Path to .app bundle
        identity: Code signing identity
    """
    try:
        # Sign with hardened runtime and timestamp
        subprocess.check_call([
            'codesign',
            '--sign', identity,
            '--force',
            '--timestamp',
            '--options', 'runtime',
            '--entitlements', 'entitlements.plist',
            '--deep',
            str(app_path)
        ])

        # Verify signature
        subprocess.check_call([
            'codesign',
            '--verify',
            '--verbose=2',
            str(app_path)
        ])

        print("✓ App signed successfully")

    except subprocess.CalledProcessError as e:
        print(f"✗ Code signing failed: {e}")
        sys.exit(1)


def notarize_macos_app(app_path: Path):
    """Notarize macOS app with Apple

    Requires:
        - APPLE_ID environment variable
        - APPLE_ID_PASSWORD environment variable (app-specific password)
        - TEAM_ID environment variable

    Args:
        app_path: Path to .app bundle
    """
    apple_id = os.getenv("APPLE_ID")
    password = os.getenv("APPLE_ID_PASSWORD")
    team_id = os.getenv("TEAM_ID")

    if not all([apple_id, password, team_id]):
        print("⚠ Skipping notarization: Missing APPLE_ID, APPLE_ID_PASSWORD, or TEAM_ID")
        return

    try:
        # Create a zip for notarization
        zip_path = app_path.with_suffix('.zip')
        subprocess.check_call([
            'ditto', '-c', '-k', '--keepParent',
            str(app_path), str(zip_path)
        ])

        # Submit for notarization
        print("Submitting to Apple for notarization...")
        result = subprocess.run([
            'xcrun', 'notarytool', 'submit', str(zip_path),
            '--apple-id', apple_id,
            '--password', password,
            '--team-id', team_id,
            '--wait'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Notarization successful")

            # Staple the ticket
            subprocess.check_call([
                'xcrun', 'stapler', 'staple', str(app_path)
            ])
            print("✓ Notarization ticket stapled")
        else:
            print(f"✗ Notarization failed:\n{result.stderr}")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"✗ Notarization failed: {e}")
        sys.exit(1)
    finally:
        # Clean up zip
        if zip_path.exists():
            zip_path.unlink()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Build Plantos MCP Installer')
    parser.add_argument('--sign', action='store_true', help='Sign the executable (macOS only)')
    parser.add_argument('--identity', help='Code signing identity')

    args = parser.parse_args()

    # Get identity from environment if not provided
    if args.sign and not args.identity:
        args.identity = os.getenv('APPLE_DEVELOPER_ID')

    build_installer(sign=args.sign, identity=args.identity)
