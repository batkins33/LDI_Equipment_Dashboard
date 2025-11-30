"""Combine PDFs from dated folders with bookmarks and logging.

This module processes PDFs organized in date-stamped folders, merging them
into single documents with bookmarks and Excel logs.
"""

from __future__ import annotations

import argparse
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

logger = logging.getLogger(__name__)


def is_date_folder(folder_name: str, pattern: str = r"\d{2}\.\d{2}\.\d{4}") -> bool:
    """Check if folder name matches date pattern.

    Parameters
    ----------
    folder_name : str
        Folder name to check
    pattern : str
        Regex pattern for date format (default: MM.DD.YYYY)

    Returns
    -------
    bool
        True if folder name matches pattern
    """
    return re.fullmatch(pattern, folder_name) is not None


def merge_pdfs_with_bookmarks(
    pdf_paths: List[Path],
    show_progress: bool = True
) -> Tuple[PdfWriter, int, pd.DataFrame]:
    """Merge PDFs and create bookmarks for each file.

    Parameters
    ----------
    pdf_paths : List[Path]
        Paths to PDF files to merge
    show_progress : bool
        Show progress bar during merging

    Returns
    -------
    Tuple[PdfWriter, int, pd.DataFrame]
        (PDF writer object, total page count, log dataframe)
    """
    writer = PdfWriter()
    log_entries = []
    page_index = 0

    iterator = tqdm(pdf_paths, desc="Merging PDFs", disable=not show_progress)

    for path in iterator:
        try:
            reader = PdfReader(path)
            num_pages = len(reader.pages)
            file_name = path.name

            # Add all pages
            for page in reader.pages:
                writer.add_page(page)

            # Add bookmark
            try:
                writer.add_outline_item(title=file_name, page_number=page_index)
            except TypeError:
                # Fallback for older pypdf versions
                writer.add_outline_item(file_name, page_index)

            log_entries.append({
                "Original File": file_name,
                "Start Page": page_index + 1,
                "Page Count": num_pages
            })

            page_index += num_pages

        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            raise

    return writer, page_index, pd.DataFrame(log_entries)


def get_output_path(
    subdir_name: str,
    page_count: int,
    output_dir: Path,
    project_code: str = "24-105",
    date_format: str = "%m.%d.%Y"
) -> Path:
    """Generate output path for combined PDF.

    Parameters
    ----------
    subdir_name : str
        Date folder name
    page_count : int
        Total pages in combined PDF
    output_dir : Path
        Base output directory
    project_code : str
        Project identifier
    date_format : str
        Date format pattern

    Returns
    -------
    Path
        Output file path with YYYY-MM structure
    """
    date_obj = datetime.strptime(subdir_name, date_format)
    ym_folder = date_obj.strftime("%Y-%m")
    output_filename = f"{project_code}_{subdir_name}_manifest_combined_{page_count}.pdf"
    return output_dir / ym_folder / output_filename


def get_log_path(output_pdf_path: Path) -> Path:
    """Get log file path corresponding to PDF output.

    Parameters
    ----------
    output_pdf_path : Path
        Path to combined PDF file

    Returns
    -------
    Path
        Excel log file path
    """
    return output_pdf_path.with_suffix(".xlsx")


def process_dated_folders(
    source_dir: Path,
    dest_dir: Path,
    project_code: str = "24-105",
    date_pattern: str = r"\d{2}\.\d{2}\.\d{4}",
    date_format: str = "%m.%d.%Y",
    sort_by_ctime: bool = True,
    verbose: bool = False
) -> int:
    """Process all dated folders in source directory.

    Parameters
    ----------
    source_dir : Path
        Source directory containing dated subfolders
    dest_dir : Path
        Destination directory for combined PDFs
    project_code : str
        Project identifier for output filenames
    date_pattern : str
        Regex pattern for date folders
    date_format : str
        Date parsing format
    sort_by_ctime : bool
        Sort by creation time (True) or filename (False)
    verbose : bool
        Enable verbose logging

    Returns
    -------
    int
        Number of folders processed successfully
    """
    if not source_dir.exists():
        logger.error(f"Source directory does not exist: {source_dir}")
        return 0

    # Find all dated subdirectories
    dated_folders = [
        subdir for subdir in source_dir.iterdir()
        if subdir.is_dir() and is_date_folder(subdir.name, date_pattern)
    ]

    if not dated_folders:
        logger.warning(f"No dated folders found in {source_dir}")
        return 0

    logger.info(f"Found {len(dated_folders)} dated folders to process")
    processed_count = 0

    for subdir in dated_folders:
        # Find PDFs in this folder
        pdf_files = [f for f in subdir.rglob("*.pdf") if f.is_file()]

        if not pdf_files:
            logger.warning(f"No PDFs found in {subdir}")
            continue

        # Sort PDFs
        if sort_by_ctime:
            pdf_files = sorted(pdf_files, key=lambda f: f.stat().st_ctime)
        else:
            pdf_files = sorted(pdf_files)

        logger.info(
            f"Processing {subdir.name}: merging {len(pdf_files)} PDFs "
            f"({'oldest to newest' if sort_by_ctime else 'alphabetically'})"
        )

        try:
            # Merge PDFs
            writer, page_count, log_df = merge_pdfs_with_bookmarks(
                pdf_files,
                show_progress=verbose
            )

            # Generate output path
            output_path = get_output_path(
                subdir.name,
                page_count,
                dest_dir,
                project_code,
                date_format
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write combined PDF
            with open(output_path, "wb") as out_file:
                writer.write(out_file)

            # Write log file
            log_path = get_log_path(output_path)
            log_df.to_excel(log_path, index=False)

            logger.info(f"Saved: {output_path} ({page_count} pages)")
            logger.info(f"Log:   {log_path}")

            processed_count += 1

        except Exception as e:
            logger.error(f"Failed to process {subdir}: {e}")
            if not verbose:
                logger.error("Use --verbose for detailed error information")
            else:
                logger.exception(e)

    return processed_count


def main():
    """CLI entry point for PDF combining."""
    parser = argparse.ArgumentParser(
        description="Combine PDFs from dated folders with bookmarks and logs"
    )
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Source directory containing dated subfolders (MM.DD.YYYY)"
    )
    parser.add_argument(
        "dest_dir",
        type=Path,
        help="Destination directory for combined PDFs"
    )
    parser.add_argument(
        "--project-code",
        type=str,
        default="24-105",
        help="Project code for output filenames (default: 24-105)"
    )
    parser.add_argument(
        "--date-pattern",
        type=str,
        default=r"\d{2}\.\d{2}\.\d{4}",
        help="Regex pattern for date folders (default: MM.DD.YYYY)"
    )
    parser.add_argument(
        "--date-format",
        type=str,
        default="%m.%d.%Y",
        help="Date format for parsing folder names (default: %%m.%%d.%%Y)"
    )
    parser.add_argument(
        "--sort-by-name",
        action="store_true",
        help="Sort by filename instead of creation time"
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
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Process folders
    processed = process_dated_folders(
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        project_code=args.project_code,
        date_pattern=args.date_pattern,
        date_format=args.date_format,
        sort_by_ctime=not args.sort_by_name,
        verbose=args.verbose
    )

    if processed > 0:
        logger.info(f"Successfully processed {processed} folders")
        return 0
    else:
        logger.error("No folders were processed successfully")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
