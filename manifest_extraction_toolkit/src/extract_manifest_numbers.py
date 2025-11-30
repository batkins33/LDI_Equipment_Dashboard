"""Extract manifest numbers from PDFs using lightweight OCR.

This module provides a simpler, faster alternative to full field extraction
when only manifest numbers are needed.
"""

from __future__ import annotations

import argparse
import io
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from PIL import Image
from tqdm import tqdm

from .config import get_config

logger = logging.getLogger(__name__)


def render_page(doc: fitz.Document, page_num: int, dpi: int = 300) -> Image.Image:
    """Render PDF page to PIL Image.

    Parameters
    ----------
    doc : fitz.Document
        PyMuPDF document object
    page_num : int
        Page number (0-indexed)
    dpi : int
        Resolution for rendering

    Returns
    -------
    Image.Image
        Rendered page as PIL Image
    """
    page = doc[page_num]
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    return Image.open(io.BytesIO(pix.tobytes(output="png")))


def extract_manifest_number(text: str) -> Optional[str]:
    """Extract 8-digit manifest number from OCR text.

    Parameters
    ----------
    text : str
        OCR text output

    Returns
    -------
    Optional[str]
        First 8-digit sequence found, or None
    """
    match = re.search(r"\b\d{8}\b", text)
    return match.group(0) if match else None


def process_pdf(
    pdf_path: Path,
    dpi: int = 300,
    max_pages: int = 3
) -> List[Dict[str, any]]:
    """Extract manifest numbers from all pages in a PDF.

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file
    dpi : int
        Resolution for rendering pages
    max_pages : int
        Maximum number of pages to process (0 = all pages)

    Returns
    -------
    List[Dict[str, any]]
        List of results with file, page, and manifest number
    """
    results = []

    try:
        with fitz.open(pdf_path) as doc:
            num_pages = len(doc) if max_pages == 0 else min(max_pages, len(doc))

            for page_num in range(num_pages):
                try:
                    img = render_page(doc, page_num, dpi=dpi)
                    text = pytesseract.image_to_string(img)
                    manifest = extract_manifest_number(text)

                    results.append({
                        "File": pdf_path.name,
                        "Page": page_num + 1,
                        "Manifest Number": manifest
                    })

                    # Stop if we found a manifest number
                    if manifest:
                        logger.debug(
                            f"Found manifest {manifest} in {pdf_path.name} page {page_num + 1}"
                        )
                        break

                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1} of {pdf_path.name}: {e}")
                    results.append({
                        "File": pdf_path.name,
                        "Page": page_num + 1,
                        "Manifest Number": None,
                        "Error": str(e)
                    })

    except Exception as e:
        logger.error(f"Error opening {pdf_path}: {e}")
        results.append({
            "File": pdf_path.name,
            "Page": 0,
            "Manifest Number": None,
            "Error": str(e)
        })

    return results


def process_directory(
    input_dir: Path,
    output_file: Path,
    dpi: int = 300,
    max_pages: int = 3,
    recursive: bool = True
) -> pd.DataFrame:
    """Process all PDFs in a directory and extract manifest numbers.

    Parameters
    ----------
    input_dir : Path
        Directory containing PDF files
    output_file : Path
        Output Excel file path
    dpi : int
        Resolution for rendering
    max_pages : int
        Maximum pages to check per PDF (0 = all)
    recursive : bool
        Search subdirectories recursively

    Returns
    -------
    pd.DataFrame
        Results dataframe
    """
    # Find all PDFs
    if recursive:
        pdf_files = sorted(input_dir.rglob("*.pdf"))
    else:
        pdf_files = sorted(input_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return pd.DataFrame()

    logger.info(f"Processing {len(pdf_files)} PDF files...")

    # Process each PDF with progress bar
    all_results = []
    for pdf_path in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        results = process_pdf(pdf_path, dpi=dpi, max_pages=max_pages)
        all_results.extend(results)

    # Create DataFrame
    df = pd.DataFrame(all_results)

    # Save to Excel
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_file, index=False)
    logger.info(f"Results saved to {output_file}")

    # Summary stats
    total_processed = len(pdf_files)
    manifests_found = df["Manifest Number"].notna().sum()
    success_rate = (manifests_found / total_processed * 100) if total_processed > 0 else 0

    logger.info(f"Summary: {manifests_found}/{total_processed} manifests found ({success_rate:.1f}%)")

    return df


def main():
    """CLI entry point for manifest number extraction."""
    parser = argparse.ArgumentParser(
        description="Extract 8-digit manifest numbers from PDFs"
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing PDF files"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output Excel file (default: manifest_numbers.xlsx)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=None,
        help="Rendering resolution (default: from config)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages to check per PDF (0=all, default: from config)"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't search subdirectories"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Load configuration
    config = get_config()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format=config.logging.format
    )

    # Set defaults from config
    dpi = args.dpi or config.ocr.dpi
    max_pages = args.max_pages if args.max_pages is not None else config.processing.max_pages_to_search
    output_file = args.output or (Path.cwd() / "manifest_numbers.xlsx")

    # Validate input
    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1

    if not args.input_dir.is_dir():
        logger.error(f"Input path is not a directory: {args.input_dir}")
        return 1

    # Process directory
    try:
        process_directory(
            input_dir=args.input_dir,
            output_file=output_file,
            dpi=dpi,
            max_pages=max_pages,
            recursive=not args.no_recursive
        )
        return 0
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
