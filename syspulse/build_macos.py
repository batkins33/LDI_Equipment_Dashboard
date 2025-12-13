#!/usr/bin/env python3
"""
Build script for macOS application bundle

Creates a standalone .app bundle using PyInstaller.

Requirements:
    pip install pyinstaller

Usage:
    python build_macos.py
"""

import subprocess
import sys
import shutil
from pathlib import Path


def build_macos():
    """Build macOS application bundle"""
    print("🔨 Building SysPulse for macOS...")
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
    print("🔧 Building application bundle...")
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
    print(f"📦 Application bundle created: dist/SysPulse.app")

    # Get bundle size
    app_path = Path('dist/SysPulse.app')
    if app_path.exists():
        # Calculate directory size
        total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        print(f"   Size: {size_mb:.1f} MB")

    print()
    print("✨ Build complete!")
    print()
    print("To distribute:")
    print("  1. Test the app: open dist/SysPulse.app")
    print("  2. Create DMG installer with create-dmg (optional)")
    print("  3. Sign and notarize the app (required for distribution)")


if __name__ == "__main__":
    build_macos()
