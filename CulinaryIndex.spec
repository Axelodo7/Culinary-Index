# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for The Culinary Index
Build with: pyinstaller CulinaryIndex.spec --clean
"""

import os
import sys
from pathlib import Path

# Use absolute path to project directory
PROJECT_DIR = Path(r"C:\Users\Ayyan\CulinaryIndex")
ASSETS_DIR = PROJECT_DIR / "assets"

# CustomTkinter data files
import customtkinter
ctk_dir = Path(os.path.dirname(customtkinter.__file__))
ctk_data = [(str(ctk_dir / "assets"), "customtkinter/assets")]

# Our assets
app_assets = [(str(ASSETS_DIR), "assets")]

# All data files
datas = ctk_data + app_assets

# Hidden imports
hiddenimports = [
    "customtkinter",
    "darkdetect",
    "requests",
    "bs4",
    "lxml",
    "ddgs",
    "duckduckgo_search",
    "primp",
    "PIL",
    "PIL.Image",
    "concurrent.futures",
    "json",
    "webbrowser",
    "threading",
]

a = Analysis(
    [str(PROJECT_DIR / "culinary_index.py")],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "email",
        "xml",
        "pydoc",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CulinaryIndex",
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
    icon=str(ASSETS_DIR / "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CulinaryIndex",
)
