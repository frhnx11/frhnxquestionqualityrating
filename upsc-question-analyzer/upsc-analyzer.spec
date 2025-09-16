# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all data from packages
datas = [
    ('templates', 'templates'),
    ('config', 'config'),
    ('src', 'src'),
    ('README_OLLAMA_SETUP.md', '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'flask',
    'ollama',
    'openpyxl',
    'rich',
    'engineio.async_drivers.threading',
    'jinja2',
    'werkzeug',
    'click',
    'question_parser',
    'ollama_analyzer',
    'excel_generator',
    'progress_tracker',
]

# Collect all package data
packages_to_collect = ['flask', 'jinja2', 'werkzeug', 'click']
for package in packages_to_collect:
    tmp_datas, tmp_binaries, tmp_hiddenimports = collect_all(package)
    datas += tmp_datas
    hiddenimports += tmp_hiddenimports

a = Analysis(
    ['app.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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

# Different settings for different platforms
if sys.platform == 'win32':
    exe_name = 'UPSC-Question-Analyzer'
    console = False  # No console window on Windows
    icon = None  # Add 'icon.ico' if you have an icon
elif sys.platform == 'darwin':
    exe_name = 'UPSC-Question-Analyzer'
    console = False
    icon = None  # Add 'icon.icns' if you have an icon
else:
    exe_name = 'upsc-question-analyzer'
    console = True  # Keep console on Linux
    icon = None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='UPSC Question Analyzer.app',
        icon=icon,
        bundle_identifier='com.upsc.analyzer',
        info_plist={
            'CFBundleName': 'UPSC Question Analyzer',
            'CFBundleDisplayName': 'UPSC Question Analyzer',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': 'True',
        },
    )