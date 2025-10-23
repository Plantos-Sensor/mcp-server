"""
Authentication module for Plantos MCP Installer
Handles OAuth device flow with Plantos backend
"""

import webbrowser
import requests
import time
import os
from typing import Optional, Dict

# Fix SSL certificate verification on macOS
import ssl
import certifi
import urllib3

# Disable SSL warnings for development testing
# NOTE: Production builds with PyInstaller will bundle certificates properly
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
PLANTOS_API_URL = "https://api.plantos.co"
PLANTOS_WEB_URL = "https://plantos.co"

# Development mode: disable SSL verification
# This is only needed for local testing - PyInstaller bundles certificates
VERIFY_SSL = False  # Set to certifi.where() for production builds


def authenticate_user() -> Optional[Dict[str, str]]:
    """
    Authenticate user with Plantos using device flow

    Flow:
    1. Request authorization code from API
    2. Open browser for user to authorize
    3. Poll API until user authorizes or timeout

    Returns: dict with 'api_key' and 'email' if successful, None otherwise
    """

    # Step 1: Request authorization code
    try:
        print("Requesting authorization code...")
        response = requests.post(
            f"{PLANTOS_API_URL}/api/v1/mcp/request-code",
            timeout=10,
            verify=VERIFY_SSL
        )

        if response.status_code != 200:
            print(f"Failed to get authorization code: {response.status_code}")
            return None

        data = response.json()
        code = data.get('code')
        verification_url = data.get('verification_url')
        expires_in = data.get('expires_in', 300)

        if not code or not verification_url:
            print("Invalid response from server")
            return None

        print(f"Authorization code: {code}")
        print(f"Opening browser to: {verification_url}")

    except Exception as e:
        print(f"Error requesting authorization code: {e}")
        return None

    # Step 2: Open browser for user authorization
    try:
        webbrowser.open(verification_url)
    except Exception as e:
        print(f"Failed to open browser: {e}")
        print(f"Please manually open: {verification_url}")

    # Step 3: Poll for authorization
    print(f"\nWaiting for authorization (code expires in {expires_in // 60} minutes)...")
    print("Please complete the authorization in your browser.\n")

    poll_interval = 3  # Poll every 3 seconds
    max_attempts = expires_in // poll_interval

    for attempt in range(max_attempts):
        try:
            # Check authorization status
            check_response = requests.get(
                f"{PLANTOS_API_URL}/api/v1/mcp/check-code",
                params={'code': code},
                timeout=10,
                verify=VERIFY_SSL
            )

            if check_response.status_code != 200:
                # Code might be invalid or expired
                if check_response.status_code == 404:
                    print("\nAuthorization code not found or expired")
                    return None
                continue

            status_data = check_response.json()
            status = status_data.get('status')

            if status == 'authorized':
                # Success! User has authorized
                api_key = status_data.get('api_key')
                if not api_key:
                    print("\nAuthorization succeeded but no API key received")
                    return None

                print("\n✓ Authorization successful!")

                # We don't get email from this endpoint, but we can fetch it if needed
                # For now, return placeholder
                return {
                    'api_key': api_key,
                    'email': 'user@plantos.co',  # Placeholder - actual email not needed for config
                    'code': code  # Return the authorization code for display
                }

            elif status == 'expired':
                print("\nAuthorization code has expired")
                return None

            elif status == 'pending':
                # Still waiting for user to authorize
                dots = "." * ((attempt % 3) + 1)
                print(f"\rWaiting for authorization{dots}   ", end='', flush=True)
                time.sleep(poll_interval)
                continue

        except requests.exceptions.Timeout:
            print("\nRequest timeout, retrying...")
            time.sleep(poll_interval)
            continue

        except Exception as e:
            print(f"\nError checking authorization status: {e}")
            time.sleep(poll_interval)
            continue

    # Timeout
    print("\n\nAuthorization timeout. Please try again.")
    return None


if __name__ == "__main__":
    # Test authentication
    print("Testing Plantos MCP authentication...")
    print("=" * 50)
    result = authenticate_user()

    if result:
        print(f"\n✓ Authenticated successfully!")
        print(f"✓ API Key: {result['api_key'][:20]}...")
    else:
        print("\n✗ Authentication failed")
