"""
Startup Manager Actions

Safe startup item management with backup and restore.
Disables/enables startup items without deleting registry entries.
"""

import os
import platform
import winreg
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import shutil


class StartupAction:
    """Result of a startup management action"""

    def __init__(self, item_name: str, action: str):
        self.item_name = item_name
        self.action = action  # 'disable', 'enable', 'backup', 'restore'
        self.success = False
        self.error = None
        self.previous_state = None

    def to_dict(self) -> Dict:
        return {
            'item_name': self.item_name,
            'action': self.action,
            'success': self.success,
            'error': self.error,
            'previous_state': self.previous_state
        }


class StartupManager:
    """Safe startup item management with backup and restore"""

    def __init__(self):
        self.system = platform.system()
        self.backup_dir = Path.home() / '.syspulse' / 'startup_backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = Path.home() / '.syspulse' / 'cleanup_log.json'

    def disable_startup_item(self, item_name: str, location: str, command: str, dry_run: bool = False) -> StartupAction:
        """
        Disable a startup item (doesn't delete, just renames)

        Args:
            item_name: Name of the startup item
            location: Registry path or folder location
            command: Command/path of the item
            dry_run: If True, only simulate

        Returns:
            StartupAction with result
        """
        action = StartupAction(item_name, 'disable')
        action.previous_state = 'enabled'

        if self.system != "Windows":
            action.error = "Startup management currently only supported on Windows"
            return action

        if dry_run:
            action.success = True
            return action

        # Backup before modifying
        backup_result = self._backup_startup_config()
        if not backup_result:
            action.error = "Failed to create backup"
            return action

        try:
            if 'Registry:' in location:
                # Handle registry startup items
                success = self._disable_registry_item(item_name, location)
                action.success = success
            elif 'Startup Folder:' in location:
                # Handle startup folder items
                success = self._disable_folder_item(item_name, location)
                action.success = success
            else:
                action.error = f"Unknown location type: {location}"

        except Exception as e:
            action.error = str(e)

        if not dry_run and action.success:
            self._log_action(action)

        return action

    def enable_startup_item(self, item_name: str, location: str, dry_run: bool = False) -> StartupAction:
        """
        Enable a previously disabled startup item

        Args:
            item_name: Name of the startup item
            location: Registry path or folder location
            dry_run: If True, only simulate

        Returns:
            StartupAction with result
        """
        action = StartupAction(item_name, 'enable')
        action.previous_state = 'disabled'

        if self.system != "Windows":
            action.error = "Startup management currently only supported on Windows"
            return action

        if dry_run:
            action.success = True
            return action

        try:
            if 'Registry:' in location:
                success = self._enable_registry_item(item_name, location)
                action.success = success
            elif 'Startup Folder:' in location:
                success = self._enable_folder_item(item_name, location)
                action.success = success
            else:
                action.error = f"Unknown location type: {location}"

        except Exception as e:
            action.error = str(e)

        if not dry_run and action.success:
            self._log_action(action)

        return action

    def _disable_registry_item(self, item_name: str, location: str) -> bool:
        """Disable a registry startup item by renaming the value"""
        try:
            # Parse registry location
            registry_path = location.replace('Registry: ', '').replace('SOFTWARE\\', '').replace('Software\\', '')

            # Determine hive
            if 'HKEY_CURRENT_USER' in location or 'Software\\Microsoft\\Windows\\CurrentVersion\\Run' in location:
                hive = winreg.HKEY_CURRENT_USER
                path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            else:
                hive = winreg.HKEY_LOCAL_MACHINE
                path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # Open registry key
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)

            try:
                # Read current value
                value, value_type = winreg.QueryValueEx(key, item_name)

                # Delete original and create disabled version
                winreg.DeleteValue(key, item_name)
                winreg.SetValueEx(key, f"_DISABLED_{item_name}", 0, value_type, value)

                return True

            finally:
                winreg.CloseKey(key)

        except Exception as e:
            print(f"Error disabling registry item: {e}")
            return False

    def _enable_registry_item(self, item_name: str, location: str) -> bool:
        """Enable a registry startup item by renaming back"""
        try:
            # Parse registry location
            if 'HKEY_CURRENT_USER' in location or 'Software\\Microsoft\\Windows\\CurrentVersion\\Run' in location:
                hive = winreg.HKEY_CURRENT_USER
                path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            else:
                hive = winreg.HKEY_LOCAL_MACHINE
                path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # Open registry key
            key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)

            try:
                # Look for disabled version
                disabled_name = f"_DISABLED_{item_name}"

                # Read disabled value
                value, value_type = winreg.QueryValueEx(key, disabled_name)

                # Delete disabled and restore original
                winreg.DeleteValue(key, disabled_name)
                winreg.SetValueEx(key, item_name, 0, value_type, value)

                return True

            finally:
                winreg.CloseKey(key)

        except Exception as e:
            print(f"Error enabling registry item: {e}")
            return False

    def _disable_folder_item(self, item_name: str, location: str) -> bool:
        """Disable a startup folder item by renaming the file"""
        try:
            # Common startup folder locations
            startup_folders = [
                Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
                Path(os.environ.get('PROGRAMDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
            ]

            for folder in startup_folders:
                if not folder.exists():
                    continue

                for item in folder.iterdir():
                    if item.stem == item_name or item.name == item_name:
                        # Rename to .disabled
                        disabled_path = item.parent / f"_DISABLED_{item.name}"
                        item.rename(disabled_path)
                        return True

            return False

        except Exception as e:
            print(f"Error disabling folder item: {e}")
            return False

    def _enable_folder_item(self, item_name: str, location: str) -> bool:
        """Enable a startup folder item by renaming back"""
        try:
            startup_folders = [
                Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
                Path(os.environ.get('PROGRAMDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
            ]

            for folder in startup_folders:
                if not folder.exists():
                    continue

                # Look for disabled version
                for item in folder.iterdir():
                    if item.name.startswith('_DISABLED_'):
                        original_name = item.name.replace('_DISABLED_', '')
                        if original_name.startswith(item_name) or item_name in original_name:
                            # Rename back to original
                            original_path = item.parent / original_name
                            item.rename(original_path)
                            return True

            return False

        except Exception as e:
            print(f"Error enabling folder item: {e}")
            return False

    def _backup_startup_config(self) -> bool:
        """Backup current startup configuration"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"startup_backup_{timestamp}.json"

            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'system': self.system,
                'registry_items': [],
                'folder_items': []
            }

            if self.system == "Windows":
                # Backup registry items
                registry_paths = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                ]

                for hive, path in registry_paths:
                    try:
                        key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
                        index = 0

                        while True:
                            try:
                                name, value, value_type = winreg.EnumValue(key, index)
                                backup_data['registry_items'].append({
                                    'hive': 'HKEY_CURRENT_USER' if hive == winreg.HKEY_CURRENT_USER else 'HKEY_LOCAL_MACHINE',
                                    'path': path,
                                    'name': name,
                                    'value': value,
                                    'type': value_type
                                })
                                index += 1
                            except OSError:
                                break

                        winreg.CloseKey(key)
                    except:
                        pass

                # Backup folder items
                startup_folders = [
                    Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
                    Path(os.environ.get('PROGRAMDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
                ]

                for folder in startup_folders:
                    if folder.exists():
                        for item in folder.iterdir():
                            if item.is_file():
                                backup_data['folder_items'].append({
                                    'folder': str(folder),
                                    'name': item.name,
                                    'path': str(item)
                                })

            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)

            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob('startup_backup_*.json'))
            for old_backup in backups[:-10]:
                old_backup.unlink()

            return True

        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def restore_from_backup(self, backup_file: Optional[Path] = None) -> bool:
        """
        Restore startup configuration from backup

        Args:
            backup_file: Specific backup to restore, or None for latest

        Returns:
            True if successful
        """
        try:
            if not backup_file:
                # Get latest backup
                backups = sorted(self.backup_dir.glob('startup_backup_*.json'))
                if not backups:
                    return False
                backup_file = backups[-1]

            with open(backup_file, 'r') as f:
                backup_data = json.load(f)

            # Restore registry items
            for item in backup_data.get('registry_items', []):
                try:
                    hive = winreg.HKEY_CURRENT_USER if item['hive'] == 'HKEY_CURRENT_USER' else winreg.HKEY_LOCAL_MACHINE
                    key = winreg.OpenKey(hive, item['path'], 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, item['name'], 0, item['type'], item['value'])
                    winreg.CloseKey(key)
                except:
                    pass

            return True

        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def list_backups(self) -> List[Dict]:
        """List available backups"""
        backups = []

        for backup_file in sorted(self.backup_dir.glob('startup_backup_*.json'), reverse=True):
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)

                backups.append({
                    'file': str(backup_file),
                    'timestamp': data.get('timestamp', 'Unknown'),
                    'size': backup_file.stat().st_size,
                    'registry_items': len(data.get('registry_items', [])),
                    'folder_items': len(data.get('folder_items', []))
                })
            except:
                pass

        return backups

    def _log_action(self, action: StartupAction):
        """Log startup management action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'startup_management',
            'result': action.to_dict()
        }

        try:
            logs = []
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)

            logs.append(log_entry)
            logs = logs[-100:]

            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception:
            pass


if __name__ == "__main__":
    # Quick test
    manager = StartupManager()

    print("Testing startup manager:\n")

    # List backups
    backups = manager.list_backups()
    print(f"Available backups: {len(backups)}")

    # Test backup creation
    print("\nCreating backup...")
    success = manager._backup_startup_config()
    print(f"Backup created: {success}")
