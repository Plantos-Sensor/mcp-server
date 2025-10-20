# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Get the MCP server script path
import os
from pathlib import Path

project_root = Path(SPECPATH)
src_dir = project_root / 'src'
mcp_server_path = src_dir / 'plantos_mcp_server.py'

a = Analysis(
    ['installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        (str(mcp_server_path), 'src'),  # Include MCP server script
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='plantos-mcp-installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file
)

# macOS: Create .app bundle
if os.name == 'posix':
    app = BUNDLE(
        exe,
        name='Plantos MCP Installer.app',
        icon=None,  # TODO: Add icon
        bundle_identifier='co.plantos.mcp-installer',
    )
