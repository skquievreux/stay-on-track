# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all customtkinter data files
datas = collect_data_files('customtkinter')

# Collect all submodules
hiddenimports = collect_submodules('customtkinter') + [
    'PIL', 'PIL._tkinter_finder', 'pystray', 'babel.numbers',
    'config', 'storage', 'ui', 'scheduler', 'version',
    'analytics', 'analytics_ui', 'category_engine'
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],  # WICHTIG: src Ordner hinzufügen!
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
    icon=None, # Add icon path here if available, e.g. 'assets/icon.ico'
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
