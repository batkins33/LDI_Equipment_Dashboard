"""Utility to organize Excel log files into logs/ subdirectories.

This script moves Excel log files from month directories into dedicated
logs/ subdirectories for better organization.
"""

from __future__ import annotations

import argparse
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def move_logs_to_subfolders(
    root_dir: Path,
    log_subdir_name: str = "logs",
    pattern: str = "*.xlsx",
    dry_run: bool = False
) -> int:
    """Move Excel files from month directories into logs/ subdirectories.

    Parameters
    ----------
    root_dir : Path
        Root directory containing month subdirectories
    log_subdir_name : str
        Name of subdirectory to create for logs (default: "logs")
    pattern : str
        File pattern to match (default: "*.xlsx")
    dry_run : bool
        If True, only show what would be moved without moving files

    Returns
    -------
    int
        Number of files moved (or would be moved in dry-run mode)
    """
    if not root_dir.exists():
        logger.error(f"Directory does not exist: {root_dir}")
        return 0

    moved_count = 0

    for month_dir in root_dir.iterdir():
        if not month_dir.is_dir():
            continue

        log_dir = month_dir / log_subdir_name

        # Find matching files in the month directory
        files = list(month_dir.glob(pattern))

        if not files:
            continue

        # Create logs subdirectory
        if not dry_run:
            log_dir.mkdir(exist_ok=True)
        else:
            logger.info(f"[DRY RUN] Would create: {log_dir}")

        # Move each file
        for file in files:
            dest = log_dir / file.name

            if dry_run:
                logger.info(f"[DRY RUN] Would move: {file.name} → {dest}")
            else:
                logger.info(f"Moving: {file.name} → {dest}")
                shutil.move(str(file), str(dest))

            moved_count += 1

    return moved_count


def main():
    """CLI entry point for log file organization."""
    parser = argparse.ArgumentParser(
        description="Move Excel log files into logs/ subdirectories"
    )
    parser.add_argument(
        "root_dir",
        type=Path,
        help="Root directory containing month subdirectories"
    )
    parser.add_argument(
        "--log-subdir",
        type=str,
        default="logs",
        help="Name of log subdirectory (default: logs)"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.xlsx",
        help="File pattern to match (default: *.xlsx)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without moving files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s - %(message)s"
    )

    # Move log files
    moved = move_logs_to_subfolders(
        root_dir=args.root_dir,
        log_subdir_name=args.log_subdir,
        pattern=args.pattern,
        dry_run=args.dry_run
    )

    if moved > 0:
        if args.dry_run:
            logger.info(f"[DRY RUN] Would move {moved} files")
        else:
            logger.info(f"Successfully moved {moved} files")
        return 0
    else:
        logger.warning("No files found to move")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
