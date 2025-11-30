"""Google Cloud Vision API extractor for invoice OCR"""

import os
from typing import Optional
from google.cloud import vision
from google.api_core import retry

from ..core.models import ExtractedInvoiceData
from .pdf_extractor import PDFExtractor


class VisionExtractor:
    """Extract invoice data using Google Cloud Vision API"""

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Vision API client

        Args:
            credentials_path: Path to Google Cloud credentials JSON
        """
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.client = vision.ImageAnnotatorClient()
        self.pdf_extractor = PDFExtractor()

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Vision API

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # Perform text detection with retry
            @retry.Retry(deadline=60)
            def detect_text():
                return self.client.text_detection(image=image)

            response = detect_text()

            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")

            texts = response.text_annotations
            if texts:
                return texts[0].description
            return ""

        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using Vision API

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            with open(pdf_path, 'rb') as pdf_file:
                content = pdf_file.read()

            # Vision API has a limit on file size
            # For large PDFs, fall back to PyPDF2
            if len(content) > 10 * 1024 * 1024:  # 10MB
                print(f"PDF too large for Vision API, using PyPDF2")
                return self.pdf_extractor.extract_text(pdf_path)

            input_config = vision.InputConfig(
                content=content,
                mime_type='application/pdf'
            )

            feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

            request = vision.AnnotateFileRequest(
                input_config=input_config,
                features=[feature]
            )

            @retry.Retry(deadline=300)
            def detect_pdf_text():
                return self.client.batch_annotate_files(requests=[request])

            response = detect_pdf_text()

            # Extract text from all pages
            text = ""
            for image_response in response.responses[0].responses:
                if image_response.full_text_annotation:
                    text += image_response.full_text_annotation.text + "\n"

            return text

        except Exception as e:
            print(f"Error extracting text from PDF with Vision API: {e}")
            # Fallback to PyPDF2
            return self.pdf_extractor.extract_text(pdf_path)

    def extract(self, file_path: str) -> ExtractedInvoiceData:
        """Extract invoice data from PDF using Vision API

        Args:
            file_path: Path to PDF file

        Returns:
            ExtractedInvoiceData with extracted fields
        """
        # Extract text using Vision API
        text = self.extract_from_pdf(file_path)

        # Use PDF extractor patterns to parse the text
        vendor_name = self.pdf_extractor.extract_vendor_name(text)
        invoice_number = self.pdf_extractor.extract_invoice_number(text)
        invoice_date = self.pdf_extractor.extract_invoice_date(text)
        total_amount = self.pdf_extractor.extract_total_amount(text)

        # Calculate confidence
        confidence = 0.0
        if vendor_name:
            confidence += 0.4
        if invoice_number:
            confidence += 0.4
        if invoice_date:
            confidence += 0.1
        if total_amount:
            confidence += 0.1

        # Vision API generally has higher confidence
        confidence = min(1.0, confidence + 0.1)

        return ExtractedInvoiceData(
            vendor_name=vendor_name,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            total_amount=total_amount,
            confidence=confidence,
            raw_text=text
        )
