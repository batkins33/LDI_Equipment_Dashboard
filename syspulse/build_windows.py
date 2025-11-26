#!/usr/bin/env python3
"""
Build script for Windows executable

Creates a standalone .exe file using PyInstaller.

Requirements:
    pip install pyinstaller

Usage:
    python build_windows.py
"""

import subprocess
import sys
import shutil
from pathlib import Path


def build_windows():
    """Build Windows executable"""
    print("🔨 Building SysPulse for Windows...")
    print()

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)

    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed {dir_name}/")

    # Build using spec file
    print()
    print("🔧 Building executable...")
    result = subprocess.run(
        ['pyinstaller', 'syspulse.spec', '--clean'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Build failed!")
        print(result.stderr)
        sys.exit(1)

    print("✅ Build successful!")
    print()
    print(f"📦 Executable created: dist/SysPulse.exe")

    # Get file size
    exe_path = Path('dist/SysPulse.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.1f} MB")

    print()
    print("✨ Build complete!")
    print()
    print("To distribute:")
    print("  1. Test the executable: dist\\SysPulse.exe")
    print("  2. Create installer with Inno Setup (optional)")
    print("  3. Sign the executable (optional)")


if __name__ == "__main__":
    build_windows()
