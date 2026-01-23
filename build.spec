# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import re

# -----------------------------------------------------------------------------
# 1. Setup Paths & Version
# -----------------------------------------------------------------------------
project_dir = os.getcwd()
src_dir = os.path.join(project_dir, 'src')

# Read version from version.py
version = "1.0.0"
try:
    with open(os.path.join(project_dir, 'version.py'), 'r') as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            version = match.group(1)
except Exception as e:
    print(f"Warning: Could not read version.py: {e}")

# Parse version for Windows format (1.0.0.0)
v_parts = version.split('.')
while len(v_parts) < 4:
    v_parts.append('0')
win_version = f"{v_parts[0]}.{v_parts[1]}.{v_parts[2]}.{v_parts[3]}"
win_version_tuple = tuple(map(int, v_parts[:4]))

# -----------------------------------------------------------------------------
# 2. Generate Version Info File
# -----------------------------------------------------------------------------
version_info_content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={win_version_tuple},
    prodvers={win_version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Quievreux Consulting'),
        StringStruct(u'FileDescription', u'Stay On Track Productivity Tool'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'StayOnTrack'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2026 Quievreux Consulting'),
        StringStruct(u'OriginalFilename', u'StayOnTrack.exe'),
        StringStruct(u'ProductName', u'Stay On Track'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

version_file_path = os.path.join(project_dir, 'file_version_info.txt')
with open(version_file_path, 'w') as f:
    f.write(version_info_content)

# -----------------------------------------------------------------------------
# 3. PyInstaller Analysis
# -----------------------------------------------------------------------------
block_cipher = None

# Collect all customtkinter data files
datas = collect_data_files('customtkinter')

# Collect all submodules
hiddenimports = collect_submodules('customtkinter') + collect_submodules('goals') + [
    'PIL', 'PIL._tkinter_finder', 'pystray', 'babel.numbers',
    # Local modules
    'config', 'storage', 'ui', 'scheduler', 'version',
    'analytics', 'analytics_ui', 'category_engine'
]

a = Analysis(
    ['src/main.py'],
    pathex=[src_dir],  # STRICTLY USE ABSOLUTE PATH
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StayOnTrack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=version_file_path, # Add metadata to EXE
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StayOnTrack',
)

