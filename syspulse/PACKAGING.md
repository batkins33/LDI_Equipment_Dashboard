# SysPulse Packaging Guide

Instructions for building standalone executables for distribution.

---

## Requirements

### All Platforms

```bash
pip install pyinstaller
```

### Platform-Specific

**Windows:**
- Inno Setup (optional, for installer creation)
- Code signing certificate (optional, for signing)

**macOS:**
- create-dmg (optional, for DMG creation)
- Apple Developer account (required for signing/notarization)

**Linux:**
- appimagetool (optional, for AppImage creation)
- dpkg-deb or rpmbuild (optional, for package creation)

---

## Building

### Windows Executable

```bash
python build_windows.py
```

**Output:** `dist/SysPulse.exe`

**Size:** ~50-80 MB (single file executable)

**Testing:**
```bash
dist\SysPulse.exe
```

### macOS Application Bundle

```bash
python build_macos.py
```

**Output:** `dist/SysPulse.app`

**Size:** ~60-90 MB (application bundle)

**Testing:**
```bash
open dist/SysPulse.app
```

### Linux Executable

```bash
python build_linux.py
```

**Output:** `dist/SysPulse`

**Size:** ~50-80 MB (single file executable)

**Testing:**
```bash
./dist/SysPulse
```

---

## Manual Build (PyInstaller)

If the build scripts don't work, use PyInstaller directly:

```bash
# Clean previous builds
pyinstaller syspulse.spec --clean

# Or without spec file
pyinstaller --onefile --windowed --name SysPulse syspulse_gui.py
```

---

## Distribution

### Windows

**Option 1: Standalone .exe**
- Simply distribute `dist/SysPulse.exe`
- No installation required
- Users can run directly

**Option 2: Installer (Inno Setup)**
1. Install Inno Setup: https://jrsoftware.org/isinfo.php
2. Create installer script (see `installer/windows.iss` example)
3. Compile installer
4. Distribute setup.exe

**Option 3: Microsoft Store**
- Package as MSIX
- Submit to Microsoft Store
- Automatic updates

### macOS

**Option 1: Standalone .app**
- Compress `dist/SysPulse.app` to ZIP
- Users extract and drag to Applications
- Requires signing for Gatekeeper

**Option 2: DMG Installer**
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "SysPulse" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "SysPulse.app" 200 190 \
  --hide-extension "SysPulse.app" \
  --app-drop-link 600 185 \
  "SysPulse-Installer.dmg" \
  "dist/"
```

**Option 3: Mac App Store**
- Package for App Store
- Submit for review
- Automatic updates

### Linux

**Option 1: Standalone executable**
- Distribute `dist/SysPulse`
- Mark as executable: `chmod +x SysPulse`
- Users can run directly

**Option 2: AppImage**
```bash
# Download appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p SysPulse.AppDir/usr/bin
cp dist/SysPulse SysPulse.AppDir/usr/bin/
# Add .desktop file and icon

# Build AppImage
./appimagetool-x86_64.AppImage SysPulse.AppDir
```

**Option 3: Package (.deb or .rpm)**
- Create debian or RPM package
- Distribute through package managers
- Easier installation for users

---

## Code Signing

### Windows

```powershell
# Sign executable
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\SysPulse.exe
```

### macOS

```bash
# Sign app
codesign --force --deep --sign "Developer ID Application: Your Name" dist/SysPulse.app

# Notarize
xcrun notarytool submit SysPulse.zip --apple-id your@email.com --wait

# Staple
xcrun stapler staple dist/SysPulse.app
```

### Linux

```bash
# GPG sign (for package verification)
gpg --detach-sign --armor dist/SysPulse
```

---

## Troubleshooting

### Build Fails

**Missing modules:**
```bash
pip install -r requirements-gui.txt
pip install pyinstaller
```

**Import errors:**
- Add missing imports to `hiddenimports` in `syspulse.spec`

**Size too large:**
- Use UPX compression (enabled in spec)
- Exclude unnecessary packages
- Use `--exclude-module` flag

### Executable Won't Run

**Windows:**
- Check antivirus (false positive)
- Run as administrator (if needed)
- Check Windows Defender SmartScreen

**macOS:**
- Sign the application
- Right-click → Open (first time)
- Check Gatekeeper settings

**Linux:**
- Make executable: `chmod +x SysPulse`
- Install missing system libraries
- Check terminal output for errors

---

## File Size Optimization

Current sizes are acceptable (<100 MB), but can be reduced:

1. **Exclude unused modules:**
   ```python
   excludes=['matplotlib', 'scipy', 'numpy']
   ```

2. **UPX compression:**
   ```python
   upx=True,
   upx_exclude=[],
   ```

3. **Strip symbols:**
   ```python
   strip=True,
   ```

4. **One-directory vs one-file:**
   - One-file is larger but more portable
   - One-directory is smaller but multiple files

---

## Auto-Update

To add auto-update functionality:

1. **Windows:** Use Squirrel.Windows or WinSparkle
2. **macOS:** Use Sparkle framework
3. **Linux:** Use AppImageUpdate or package managers
4. **Cross-platform:** Implement custom update checker

Example update check:
```python
import requests

def check_for_updates():
    response = requests.get('https://api.example.com/version')
    latest_version = response.json()['version']
    current_version = '3.0.0-alpha.9'

    if latest_version > current_version:
        # Notify user of update
        pass
```

---

## Release Checklist

Before distributing:

- [ ] Test on clean system (no Python installed)
- [ ] Verify all features work
- [ ] Check file size is reasonable
- [ ] Sign executable (Windows/macOS)
- [ ] Create installer (optional)
- [ ] Write release notes
- [ ] Tag version in git
- [ ] Upload to distribution platform
- [ ] Update website/documentation

---

## Distribution Platforms

- **GitHub Releases** - Free, version control integration
- **SourceForge** - Traditional, analytics
- **Microsoft Store** - Windows, automatic updates
- **Mac App Store** - macOS, automatic updates
- **Snapcraft** - Linux, automatic updates
- **Flathub** - Linux, Flatpak distribution

---

**Last Updated:** 2025-01-26
**Version:** 3.0.0-alpha.9
