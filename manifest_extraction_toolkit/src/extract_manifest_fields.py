"""Anchor-based OCR pipeline for manifest field extraction.

Replaces the "full-page OCR + regex" approach with precise ROI extraction
using anchor-based positioning for structured field extraction.
"""

from __future__ import annotations

import functools
import io
import logging
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import pandas as pd
import pytesseract
from PIL import Image, ImageFilter, ImageOps
from pytesseract import Output
from tqdm import tqdm

from .config import get_config

logger = logging.getLogger(__name__)

# Global cache for rendered pages
_page_cache: Dict[str, Image.Image] = {}
_cache_enabled = True


def set_cache_enabled(enabled: bool):
    """Enable or disable page rendering cache."""
    global _cache_enabled
    _cache_enabled = enabled


def clear_cache():
    """Clear the page rendering cache."""
    global _page_cache
    _page_cache.clear()


# ---------- Helper Functions ----------


def render_page(doc: fitz.Document, pno: int, dpi: int = 300, use_cache: bool = True) -> Image.Image:
    """Render PDF page to PIL Image with optional caching.

    Parameters
    ----------
    doc : fitz.Document
        PyMuPDF document object
    pno : int
        Page number (0-indexed)
    dpi : int
        Resolution for rendering
    use_cache : bool
        Use cached renders if available

    Returns
    -------
    Image.Image
        Rendered page image
    """
    config = get_config()

    if use_cache and config.performance.enable_caching and _cache_enabled:
        # Create cache key from document path and page number
        cache_key = f"{id(doc)}_{pno}_{dpi}"
        if cache_key in _page_cache:
            return _page_cache[cache_key]

    page = doc[pno]
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes(output="png")))

    if use_cache and config.performance.enable_caching and _cache_enabled:
        _page_cache[cache_key] = img

    return img


def ocr_words(img: Image.Image) -> pd.DataFrame:
    """Extract word-level OCR data with bounding boxes.

    Parameters
    ----------
    img : Image.Image
        Page image

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: text, left, top, width, height, right, bottom
    """
    df = pytesseract.image_to_data(img, output_type=Output.DATAFRAME)
    df = df.dropna(subset=["text"]).copy()
    df["right"] = df["left"] + df["width"]
    df["bottom"] = df["top"] + df["height"]
    return df


def find_line_anchor(words: pd.DataFrame, needed: List[str], y_tolerance: int = 10) -> Optional[Tuple[int, int, int, int]]:
    """Find a line that contains all required tokens (case-insensitive).

    Parameters
    ----------
    words : pd.DataFrame
        OCR word dataframe
    needed : List[str]
        Required tokens to find
    y_tolerance : int
        Vertical tolerance for line grouping

    Returns
    -------
    Optional[Tuple[int, int, int, int]]
        (x0, y0, x1, y1) bounding box of matched tokens, or None
    """
    grp_cols = ["page_num", "block_num", "par_num", "line_num"]

    for _, line in words.groupby(grp_cols):
        tokens = " ".join(line["text"].astype(str).tolist()).lower()
        if all(tok.lower() in tokens for tok in needed):
            x0 = int(line["left"].min())
            y0 = int(line["top"].min())
            x1 = int(line["right"].max())
            y1 = int(line["bottom"].max())
            return (x0, y0, x1, y1)

    return None


def crop(img: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
    """Crop image to bounding box, clamping to image bounds.

    Parameters
    ----------
    img : Image.Image
        Source image
    box : Tuple[int, int, int, int]
        (x0, y0, x1, y1) bounding box

    Returns
    -------
    Image.Image
        Cropped image
    """
    w, h = img.size
    x0, y0, x1, y1 = box
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(w, x1)
    y1 = min(h, y1)

    # Ensure valid crop region
    if x1 <= x0 or y1 <= y0:
        logger.warning(f"Invalid crop box after clamping: ({x0},{y0},{x1},{y1})")
        return img

    return img.crop((x0, y0, x1, y1))


def binarize_for_handwriting(im: Image.Image, threshold: int = None) -> Image.Image:
    """Apply strong binarization for handwriting OCR.

    Parameters
    ----------
    im : Image.Image
        Source image
    threshold : int
        Binarization threshold (default: from config)

    Returns
    -------
    Image.Image
        Binarized image
    """
    config = get_config()
    if threshold is None:
        threshold = config.handwriting.binarization_threshold

    g = ImageOps.grayscale(im)
    g = g.filter(ImageFilter.MedianFilter(size=config.handwriting.median_filter_size))
    return g.point(lambda p: 255 if p > threshold else 0)


def ocr_text(im: Image.Image, digits_only: bool = False, single_line: bool = False) -> str:
    """OCR text from image region.

    Parameters
    ----------
    im : Image.Image
        Image to OCR
    digits_only : bool
        Restrict to digits only
    single_line : bool
        Use single-line PSM mode

    Returns
    -------
    str
        Extracted text
    """
    config = get_config()
    cfg = []

    if digits_only:
        cfg.append("tessedit_char_whitelist=0123456789")

    psm = config.ocr.tesseract_psm_single_line if single_line else config.ocr.tesseract_psm_block
    oem = config.ocr.tesseract_oem

    return pytesseract.image_to_string(
        im, config=f"--oem {oem} --psm {psm} " + ("-c " + " ".join(cfg) if cfg else "")
    ).strip()


# ---------- ROI Functions ----------


def right_of(anchor: Tuple[int, int, int, int], dx: int = 10, w: int = 220, dy: int = -5, h: int = 36) -> Tuple[int, int, int, int]:
    """Create ROI to the right of anchor.

    FIXED: Properly handle negative dy values.

    Parameters
    ----------
    anchor : Tuple[int, int, int, int]
        Anchor bounding box (x0, y0, x1, y1)
    dx : int
        Horizontal offset from anchor right edge
    w : int
        ROI width
    dy : int
        Vertical offset from anchor top (can be negative)
    h : int
        ROI height

    Returns
    -------
    Tuple[int, int, int, int]
        ROI bounding box (x0, y0, x1, y1)
    """
    ax0, ay0, ax1, ay1 = anchor
    x0 = ax1 + dx
    y0 = ay0 + dy
    x1 = x0 + w
    y1 = y0 + h
    return (x0, y0, x1, y1)


def below_band(anchor: Tuple[int, int, int, int], img: Image.Image, top_pad: int = 8, bottom: int = 70, left: float = 0.08, right: float = 0.62) -> Tuple[int, int, int, int]:
    """Create band ROI below anchor.

    Parameters
    ----------
    anchor : Tuple[int, int, int, int]
        Anchor bounding box
    img : Image.Image
        Page image for dimensions
    top_pad : int
        Padding below anchor
    bottom : int
        Height of band
    left : float
        Left edge as fraction of page width
    right : float
        Right edge as fraction of page width

    Returns
    -------
    Tuple[int, int, int, int]
        ROI bounding box
    """
    W, H = img.size
    ax0, ay0, ax1, ay1 = anchor
    y0 = ay1 + top_pad
    y1 = min(H, y0 + bottom)
    return (int(W * left), y0, int(W * right), y1)


# ---------- Field Validation/Cleaning ----------


_manifest_re = re.compile(r"^\d{8}$")
plate_re = re.compile(r"[A-Z0-9]{2,8}(?:-[A-Z0-9]{1,4})?$", re.I)
dot_num_re = re.compile(r"(?:US\s*DOT|USDOT|DOT)\D*(\d{4,9})", re.I)


def clean_manifest(s: str) -> str:
    """Validate manifest number as exactly 8 digits."""
    s = re.sub(r"[^\d]", "", s)
    return s if _manifest_re.match(s) else ""


def clean_plate(s: str) -> str:
    """Normalize license plate to uppercase.

    FIXED: Don't truncate to 10 chars if pattern doesn't match.
    """
    s = s.replace(" ", "").upper()
    cand = plate_re.findall(s)
    if cand:
        return cand[0]

    # Return cleaned string (no truncation) or empty if too long/short
    if 2 <= len(s) <= 12:
        return s
    else:
        logger.warning(f"Invalid license plate length: '{s}' ({len(s)} chars)")
        return ""


def clean_dot(s: str) -> str:
    """Extract DOT ID number, prefer USDOT format."""
    m = dot_num_re.search(s)
    if m:
        return m.group(1)

    # Fallback: take a 4-9 digit run
    m2 = re.search(r"\b\d{4,9}\b", s)
    return m2.group(0) if m2 else s.strip()


def normalize_phone(s: str) -> str:
    """Normalize phone to (xxx) xxx-xxxx format when possible."""
    config = get_config()
    digits = re.sub(r"[^\d]", "", s)

    if len(digits) == config.validation.get("phone_length", 10):
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    return s.strip()


def pass_through(s: str) -> str:
    """Basic text cleaning - normalize whitespace."""
    return " ".join(s.split())


# ---------- Field Specifications ----------


@dataclass
class FieldSpec:
    """Specification for extracting a single field."""
    name: str
    anchor_tokens: List[str]
    roi_from_anchor: callable
    post: callable


def build_field_specs(config) -> List[FieldSpec]:
    """Build field specifications from configuration."""
    specs = []

    # Manifest Number
    mn_cfg = config.fields.get("manifest_number", {})
    specs.append(
        FieldSpec(
            name="manifest_number",
            anchor_tokens=config.anchors.get("manifest_number", ["manifest", "number"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc,
                dx=mn_cfg.get("dx", 12),
                w=mn_cfg.get("w", 200),
                dy=mn_cfg.get("dy", -2),
                h=mn_cfg.get("h", 40)
            ),
            post=clean_manifest,
        )
    )

    # Transporter 1 fields
    t1_company_cfg = config.fields.get("transporter_company", {})
    specs.append(
        FieldSpec(
            name="t1_company",
            anchor_tokens=config.anchors.get("t1_company", ["transporter", "1", "company", "name"]),
            roi_from_anchor=lambda img, anc: below_band(
                anc, img,
                top_pad=t1_company_cfg.get("top_pad", 8),
                bottom=t1_company_cfg.get("bottom", 80),
                left=t1_company_cfg.get("left", 0.08),
                right=t1_company_cfg.get("right", 0.62)
            ),
            post=pass_through,
        )
    )

    epa_cfg = config.fields.get("epa_id", {})
    specs.extend([
        FieldSpec(
            name="t1_us_epa_id",
            anchor_tokens=config.anchors.get("t1_us_epa_id", ["us", "epa", "id", "number"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc, dx=epa_cfg.get("dx", 8), w=epa_cfg.get("w", 220),
                dy=epa_cfg.get("dy", 4), h=epa_cfg.get("h", 32)
            ),
            post=pass_through,
        ),
    ])

    state_cfg = config.fields.get("state_id", {})
    specs.append(
        FieldSpec(
            name="t1_state_id",
            anchor_tokens=config.anchors.get("t1_state_id", ["state", "id"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc, dx=state_cfg.get("dx", 8), w=state_cfg.get("w", 220),
                dy=state_cfg.get("dy", 4), h=state_cfg.get("h", 32)
            ),
            post=pass_through,
        )
    )

    phone_cfg = config.fields.get("phone", {})
    specs.append(
        FieldSpec(
            name="t1_phone",
            anchor_tokens=config.anchors.get("t1_phone", ["phone"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc, dx=phone_cfg.get("dx", 8), w=phone_cfg.get("w", 220),
                dy=phone_cfg.get("dy", 4), h=phone_cfg.get("h", 32)
            ),
            post=normalize_phone,
        )
    )

    # Transporter 2 fields (same structure)
    specs.extend([
        FieldSpec(
            name="t2_company",
            anchor_tokens=config.anchors.get("t2_company", ["transporter", "2", "company", "name"]),
            roi_from_anchor=lambda img, anc: below_band(
                anc, img,
                top_pad=t1_company_cfg.get("top_pad", 8),
                bottom=t1_company_cfg.get("bottom", 80),
                left=t1_company_cfg.get("left", 0.08),
                right=t1_company_cfg.get("right", 0.62)
            ),
            post=pass_through,
        ),
        FieldSpec(
            name="t2_us_epa_id",
            anchor_tokens=config.anchors.get("t2_us_epa_id", ["us", "epa", "id", "number"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc, dx=epa_cfg.get("dx", 8), w=epa_cfg.get("w", 220),
                dy=epa_cfg.get("dy", 4), h=epa_cfg.get("h", 32)
            ),
            post=pass_through,
        ),
        FieldSpec(
            name="t2_state_id",
            anchor_tokens=config.anchors.get("t2_state_id", ["state", "id"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc, dx=state_cfg.get("dx", 8), w=state_cfg.get("w", 220),
                dy=state_cfg.get("dy", 4), h=state_cfg.get("h", 32)
            ),
            post=pass_through,
        ),
        FieldSpec(
            name="t2_phone",
            anchor_tokens=config.anchors.get("t2_phone", ["phone"]),
            roi_from_anchor=lambda img, anc: right_of(
                anc, dx=phone_cfg.get("dx", 8), w=phone_cfg.get("w", 220),
                dy=phone_cfg.get("dy", 4), h=phone_cfg.get("h", 32)
            ),
            post=normalize_phone,
        ),
    ])

    return specs


def extract_handwritten_bottom(img: Image.Image) -> Dict[str, str]:
    """Extract handwritten fields from bottom band of page.

    Parameters
    ----------
    img : Image.Image
        Page image

    Returns
    -------
    Dict[str, str]
        Extracted fields: license_plate, dot_id, truck_number
    """
    config = get_config()
    hw_cfg = config.handwriting

    W, H = img.size

    # Extract bottom band
    band = crop(
        img,
        (
            int(W * hw_cfg.bottom_band_left_percent),
            int(H * hw_cfg.bottom_band_top_percent),
            int(W * hw_cfg.bottom_band_right_percent),
            int(H * hw_cfg.bottom_band_bottom_percent),
        )
    )

    # Split into 3 columns
    cols = []
    for i in range(3):
        x0 = int(band.width * (i / 3))
        x1 = int(band.width * ((i + 1) / 3))
        cols.append(band.crop((x0, 0, x1, band.height)))

    # Preprocess for handwriting
    cols = [binarize_for_handwriting(c) for c in cols]

    plate_txt = ocr_text(cols[0], single_line=True)
    dot_txt = ocr_text(cols[1], single_line=True)
    truck_txt = ocr_text(cols[2], single_line=True)

    return {
        "license_plate": clean_plate(plate_txt),
        "dot_id": clean_dot(dot_txt),
        "truck_number": pass_through(truck_txt),
    }


def extract_fields_from_page(img: Image.Image, field_specs: List[FieldSpec] = None) -> Dict[str, str]:
    """Extract all fields from a single page using anchor-based ROI extraction.

    Parameters
    ----------
    img : Image.Image
        Page image
    field_specs : List[FieldSpec]
        Field specifications (default: build from config)

    Returns
    -------
    Dict[str, str]
        Extracted field values
    """
    if field_specs is None:
        config = get_config()
        field_specs = build_field_specs(config)

    words = ocr_words(img)
    out = {}

    for spec in field_specs:
        anc = find_line_anchor(words, spec.anchor_tokens)
        if not anc:
            logger.warning(f"Anchor not found for {spec.name}: {spec.anchor_tokens}")
            out[spec.name] = ""
            continue

        roi = spec.roi_from_anchor(img, anc)
        crop_im = crop(img, roi)

        digits_only = spec.name == "manifest_number"
        single_line = spec.name.startswith(
            ("t1_us_epa_id", "t2_us_epa_id", "t1_state_id", "t2_state_id", "t1_phone", "t2_phone", "manifest_number")
        )

        try:
            raw_txt = ocr_text(crop_im, digits_only=digits_only, single_line=single_line)
            cleaned = spec.post(raw_txt)
            out[spec.name] = cleaned

            if not cleaned and raw_txt:
                logger.warning(f"Validation failed for {spec.name}: '{raw_txt}'")

        except Exception as e:
            logger.error(f"OCR failed for {spec.name}: {e}")
            out[spec.name] = ""

    # Extract handwritten fields
    out.update(extract_handwritten_bottom(img))

    return out


def process_pdf(pdf_path: Path) -> Dict[str, str]:
    """Process PDF and extract manifest fields from first valid page.

    Parameters
    ----------
    pdf_path : Path
        Path to PDF file

    Returns
    -------
    Dict[str, str]
        Extracted field values with source_file and page metadata
    """
    config = get_config()

    # Validate file size
    if not config.validate_file_size(pdf_path):
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        logger.error(
            f"File {pdf_path.name} ({size_mb:.1f}MB) exceeds size limit "
            f"({config.processing.max_file_size_mb}MB)"
        )
        return {"source_file": pdf_path.name, "page": 0, "error": "File too large"}

    try:
        with fitz.open(pdf_path) as doc:
            # Try first N pages for anchors
            max_pages = config.processing.max_pages_to_search
            num_pages = min(max_pages, len(doc)) if max_pages > 0 else len(doc)

            for pno in range(num_pages):
                img = render_page(doc, pno, dpi=config.ocr.dpi)
                fields = extract_fields_from_page(img)

                # Validate manifest number found
                if fields.get("manifest_number"):
                    fields["source_file"] = pdf_path.name
                    fields["page"] = pno + 1
                    return fields

            # Fallback to page 1 if no manifest anchor found
            img = render_page(doc, 0, dpi=config.ocr.dpi)
            fields = extract_fields_from_page(img)
            fields["source_file"] = pdf_path.name
            fields["page"] = 1
            logger.warning(f"No manifest anchor found in {pdf_path.name}, using page 1 fallback")
            return fields

    except Exception as e:
        logger.error(f"Failed to process {pdf_path}: {e}")
        return {"source_file": pdf_path.name, "page": 1, "error": str(e)}


def process_pdf_wrapper(pdf_path: Path) -> Dict[str, str]:
    """Wrapper for multiprocessing (top-level function)."""
    return process_pdf(pdf_path)


def main(src_dir: str, out_xlsx: str, parallel: bool = None, max_workers: int = None):
    """Main function to process directory of PDFs and extract manifest fields.

    Parameters
    ----------
    src_dir : str
        Source directory containing PDFs
    out_xlsx : str
        Output Excel file path
    parallel : bool
        Enable parallel processing (default: from config)
    max_workers : int
        Number of worker processes (default: from config)
    """
    config = get_config()
    src_path = Path(src_dir)
    pdfs = sorted(src_path.rglob("*.pdf"))

    if not pdfs:
        logger.warning(f"No PDF files found in {src_dir}")
        return

    logger.info(f"Processing {len(pdfs)} PDF files...")

    # Determine parallelization settings
    use_parallel = parallel if parallel is not None else config.performance.enable_parallel
    workers = max_workers or config.performance.max_workers

    rows = []

    if use_parallel and len(pdfs) > 1:
        logger.info(f"Using parallel processing with {workers} workers")
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_pdf_wrapper, p): p for p in pdfs}

            for future in tqdm(as_completed(futures), total=len(pdfs), desc="Processing PDFs"):
                try:
                    result = future.result()
                    rows.append(result)
                except Exception as e:
                    pdf = futures[future]
                    logger.error(f"Error processing {pdf}: {e}")
                    rows.append({"source_file": pdf.name, "error": str(e)})
    else:
        # Sequential processing with progress bar
        for p in tqdm(pdfs, desc="Processing PDFs"):
            result = process_pdf(p)
            rows.append(result)

    # Create DataFrame with specified column order
    columns = [
        "source_file",
        "page",
        "manifest_number",
        "t1_company",
        "t1_us_epa_id",
        "t1_state_id",
        "t1_phone",
        "t2_company",
        "t2_us_epa_id",
        "t2_state_id",
        "t2_phone",
        "license_plate",
        "dot_id",
        "truck_number",
    ]

    df = pd.DataFrame(rows)

    # Reorder columns, add missing ones as empty
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    df = df[columns + [c for c in df.columns if c not in columns]]

    # Save results
    output_path = Path(out_xlsx)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)

    logger.info(f"Results saved to {output_path}")
    print(f"Saved: {output_path}")

    # Clear cache to free memory
    clear_cache()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract manifest fields using anchor-based OCR")
    parser.add_argument("src", help="Source directory containing PDF files (recurses)")
    parser.add_argument("--out", default="manifest_fields.xlsx", help="Output Excel file")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")
    parser.add_argument("--workers", type=int, default=None, help="Number of workers for parallel processing")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    main(args.src, args.out, parallel=args.parallel, max_workers=args.workers)
