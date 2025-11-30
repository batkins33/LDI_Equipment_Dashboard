"""Summarize page counts from PDF combination logs.

This script aggregates page counts from Excel log files, grouping by
month, week, and day for analysis and reporting.
"""

from __future__ import annotations

import argparse
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def find_log_files(
    root_dir: Path,
    pattern: str = "**/*manifest_combined*.xlsx",
    recursive: bool = True
) -> List[Path]:
    """Find all log files matching pattern.

    Parameters
    ----------
    root_dir : Path
        Root directory to search
    pattern : str
        Glob pattern for log files
    recursive : bool
        Search recursively (default: True)

    Returns
    -------
    List[Path]
        List of log file paths
    """
    if recursive:
        return list(root_dir.rglob(pattern))
    else:
        return list(root_dir.glob(pattern))


def extract_date_from_filename(
    filename: str,
    pattern: str = r"(\d{2}\.\d{2}\.\d{4})",
    date_format: str = "%m.%d.%Y"
) -> Optional[datetime]:
    """Extract date from filename using regex pattern.

    Parameters
    ----------
    filename : str
        Filename to parse
    pattern : str
        Regex pattern with one capture group for date
    date_format : str
        Date format for parsing

    Returns
    -------
    Optional[datetime]
        Parsed datetime object, or None if not found
    """
    match = re.search(pattern, filename)
    if not match:
        return None

    try:
        return datetime.strptime(match.group(1), date_format)
    except ValueError as e:
        logger.warning(f"Failed to parse date from {filename}: {e}")
        return None


def process_log_files(
    log_files: List[Path],
    date_pattern: str = r"(\d{2}\.\d{2}\.\d{4})",
    date_format: str = "%m.%d.%Y"
) -> pd.DataFrame:
    """Process log files and extract page count summaries.

    Parameters
    ----------
    log_files : List[Path]
        Paths to Excel log files
    date_pattern : str
        Regex pattern for extracting date from filename
    date_format : str
        Date format for parsing

    Returns
    -------
    pd.DataFrame
        Combined dataframe with Month, Week, Day, and aggregated page counts
    """
    all_data = []

    for log_file in log_files:
        # Extract date from filename
        date_obj = extract_date_from_filename(log_file.name, date_pattern, date_format)

        if not date_obj:
            logger.warning(f"Skipping {log_file.name}: Could not extract date")
            continue

        # Format date components
        month = date_obj.strftime("%Y-%m")
        week = date_obj.strftime("Week %U")  # Week starting on Sunday
        day = date_obj.strftime("%m.%d.%Y")

        # Read log file
        try:
            df = pd.read_excel(log_file)

            # Add date dimensions
            df["Date"] = day
            df["Month"] = month
            df["Week"] = week
            df["Day"] = day

            # Keep relevant columns
            cols_to_keep = ["Original File", "Page Count", "Month", "Week", "Day"]
            available_cols = [c for c in cols_to_keep if c in df.columns]

            if "Page Count" not in available_cols:
                logger.warning(f"Skipping {log_file.name}: No 'Page Count' column")
                continue

            all_data.append(df[available_cols])

        except Exception as e:
            logger.error(f"Failed to read {log_file}: {e}")

    if not all_data:
        logger.warning("No valid log files processed")
        return pd.DataFrame()

    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df


def create_pivot_summary(
    df: pd.DataFrame,
    group_by: List[str] = None
) -> pd.DataFrame:
    """Create pivot table summary of page counts.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with page counts
    group_by : List[str]
        Columns to group by (default: ["Month", "Week", "Day"])

    Returns
    -------
    pd.DataFrame
        Pivot table with aggregated page counts
    """
    if group_by is None:
        group_by = ["Month", "Week", "Day"]

    # Filter to only columns that exist
    available_groups = [g for g in group_by if g in df.columns]

    if not available_groups:
        logger.error("No grouping columns found")
        return pd.DataFrame()

    # Group and sum page counts
    pivot = df.groupby(available_groups)["Page Count"].sum().reset_index()
    return pivot


def main():
    """CLI entry point for page count summarization."""
    parser = argparse.ArgumentParser(
        description="Summarize page counts from PDF combination logs"
    )
    parser.add_argument(
        "root_dir",
        type=Path,
        help="Root directory containing log files"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output Excel file (default: combined_manifest_summary.xlsx)"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*manifest_combined*.xlsx",
        help="Glob pattern for log files (default: **/*manifest_combined*.xlsx)"
    )
    parser.add_argument(
        "--date-pattern",
        type=str,
        default=r"(\d{2}\.\d{2}\.\d{4})",
        help="Regex pattern for extracting date from filename"
    )
    parser.add_argument(
        "--date-format",
        type=str,
        default="%m.%d.%Y",
        help="Date format for parsing (default: %%m.%%d.%%Y)"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't search subdirectories recursively"
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

    # Set output file
    output_file = args.output or (args.root_dir / "combined_manifest_summary.xlsx")

    # Find log files
    logger.info(f"Searching for log files in {args.root_dir}")
    log_files = find_log_files(
        args.root_dir,
        pattern=args.pattern,
        recursive=not args.no_recursive
    )

    if not log_files:
        logger.error(f"No log files found matching pattern: {args.pattern}")
        return 1

    logger.info(f"Found {len(log_files)} log files")

    # Process log files
    combined_df = process_log_files(
        log_files,
        date_pattern=args.date_pattern,
        date_format=args.date_format
    )

    if combined_df.empty:
        logger.error("No data extracted from log files")
        return 1

    # Create pivot summary
    pivot = create_pivot_summary(combined_df)

    if pivot.empty:
        logger.error("Failed to create pivot summary")
        return 1

    # Save output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    pivot.to_excel(output_file, index=False)
    logger.info(f"Saved summary to: {output_file}")

    # Display summary stats
    total_pages = pivot["Page Count"].sum()
    logger.info(f"Total pages across all logs: {total_pages:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
