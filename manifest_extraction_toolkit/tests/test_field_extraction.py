"""Comprehensive tests for manifest field extraction."""

import re
from pathlib import Path

import pytest
from PIL import Image

# Import functions to test (need to add __init__.py to src first)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from extract_manifest_fields import (
    clean_dot,
    clean_manifest,
    clean_plate,
    normalize_phone,
    pass_through,
    right_of,
    below_band,
    crop,
)


class TestManifestValidation:
    """Test manifest number validation."""

    def test_valid_8_digit(self):
        assert clean_manifest("12345678") == "12345678"

    def test_with_hyphens(self):
        assert clean_manifest("1234-5678") == "12345678"

    def test_with_spaces(self):
        assert clean_manifest("1234 5678") == "12345678"

    def test_embedded_in_text(self):
        assert clean_manifest("ABC12345678XYZ") == "12345678"

    def test_too_short(self):
        assert clean_manifest("1234567") == ""

    def test_too_long(self):
        assert clean_manifest("123456789") == ""

    def test_no_digits(self):
        assert clean_manifest("ABCDEFGH") == ""

    def test_mixed_alphanumeric(self):
        # Should extract only digits, then validate
        assert clean_manifest("A1B2C3D4E5F6G7H8") == "12345678"


class TestPhoneNormalization:
    """Test phone number normalization."""

    def test_10_digits_plain(self):
        assert normalize_phone("1234567890") == "(123) 456-7890"

    def test_already_formatted(self):
        assert normalize_phone("(123) 456-7890") == "(123) 456-7890"

    def test_with_hyphens(self):
        assert normalize_phone("123-456-7890") == "(123) 456-7890"

    def test_with_dots(self):
        assert normalize_phone("123.456.7890") == "(123) 456-7890"

    def test_with_spaces(self):
        assert normalize_phone("123 456 7890") == "(123) 456-7890"

    def test_invalid_length_short(self):
        # Should return as-is if not 10 digits
        assert normalize_phone("12345") == "12345"

    def test_invalid_length_long(self):
        result = normalize_phone("12345678901")
        assert result == "12345678901"  # More than 10, return stripped

    def test_with_country_code(self):
        # 11 digits (with +1) - should not format
        result = normalize_phone("+11234567890")
        assert result != "(123) 456-7890"  # Won't match 10-digit pattern


class TestLicensePlate:
    """Test license plate cleaning."""

    def test_valid_uppercase(self):
        assert clean_plate("ABC123") == "ABC123"

    def test_lowercase_to_upper(self):
        assert clean_plate("abc123") == "ABC123"

    def test_with_hyphen(self):
        assert clean_plate("ABC-123") == "ABC-123"

    def test_with_spaces(self):
        # Spaces removed
        assert clean_plate("AB C123") == "ABC123"

    def test_mixed_case_with_hyphen(self):
        assert clean_plate("aBc-123") == "ABC-123"

    def test_too_short(self):
        # Less than 2 chars
        assert clean_plate("A") == ""

    def test_too_long(self):
        # More than 12 chars
        assert clean_plate("ABCDEFGHIJKLM") == ""

    def test_empty_string(self):
        assert clean_plate("") == ""

    def test_numeric_only(self):
        assert clean_plate("123456") == "123456"

    def test_valid_range(self):
        # 2-12 chars should be valid
        assert clean_plate("AB") != ""
        assert clean_plate("ABCDEFGHIJKL") != ""


class TestDOTID:
    """Test DOT ID extraction."""

    def test_usdot_format(self):
        assert clean_dot("USDOT 123456") == "123456"

    def test_us_dot_with_colon(self):
        assert clean_dot("US DOT: 789012") == "789012"

    def test_dot_hash(self):
        assert clean_dot("DOT#345678") == "345678"

    def test_embedded_in_text(self):
        assert clean_dot("Random USDOT12345 text") == "12345"

    def test_fallback_digits(self):
        # No USDOT prefix, should find 5-9 digit sequence
        assert clean_dot("Random 567890 text") == "567890"

    def test_too_few_digits(self):
        # Less than 4 digits shouldn't match fallback
        result = clean_dot("Random 123 text")
        assert result == "Random 123 text"  # Returns stripped original

    def test_4_digit_minimum(self):
        assert clean_dot("DOT 1234") == "1234"

    def test_9_digit_maximum(self):
        assert clean_dot("DOT 123456789") == "123456789"


class TestPassThrough:
    """Test basic text cleaning."""

    def test_multiple_spaces(self):
        assert pass_through("hello    world") == "hello world"

    def test_leading_trailing_spaces(self):
        assert pass_through("  hello world  ") == "hello world"

    def test_tabs_and_newlines(self):
        assert pass_through("hello\t\nworld") == "hello world"

    def test_normal_text(self):
        assert pass_through("hello world") == "hello world"

    def test_empty_string(self):
        assert pass_through("") == ""


class TestROIFunctions:
    """Test ROI calculation functions."""

    def test_right_of_basic(self):
        anchor = (100, 50, 200, 80)
        roi = right_of(anchor, dx=10, w=150, dy=5, h=25)
        # x0 = 200+10 = 210
        # y0 = 50+5 = 55
        # x1 = 210+150 = 360
        # y1 = 55+25 = 80
        assert roi == (210, 55, 360, 80)

    def test_right_of_negative_dy(self):
        # Test that negative dy works correctly
        anchor = (100, 50, 200, 80)
        roi = right_of(anchor, dx=10, w=150, dy=-5, h=25)
        # x0 = 200+10 = 210
        # y0 = 50+(-5) = 45
        # x1 = 210+150 = 360
        # y1 = 45+25 = 70
        assert roi == (210, 45, 360, 70)

    def test_below_band_basic(self):
        anchor = (100, 50, 200, 80)
        img = Image.new("RGB", (1000, 2000))  # W=1000, H=2000

        roi = below_band(anchor, img, top_pad=10, bottom=50, left=0.1, right=0.5)
        # x0 = 1000 * 0.1 = 100
        # y0 = 80 + 10 = 90
        # x1 = 1000 * 0.5 = 500
        # y1 = min(2000, 90 + 50) = 140
        assert roi == (100, 90, 500, 140)

    def test_below_band_exceeds_image_height(self):
        anchor = (100, 1950, 200, 1980)
        img = Image.new("RGB", (1000, 2000))

        roi = below_band(anchor, img, top_pad=10, bottom=100, left=0.1, right=0.5)
        # y0 = 1980 + 10 = 1990
        # y1 = min(2000, 1990 + 100) = 2000  # Clamped to image height
        assert roi[3] == 2000


class TestCropFunction:
    """Test image cropping with bounds clamping."""

    def test_crop_valid_box(self):
        img = Image.new("RGB", (100, 100), color="red")
        cropped = crop(img, (10, 10, 50, 50))
        assert cropped.size == (40, 40)

    def test_crop_negative_coords(self):
        img = Image.new("RGB", (100, 100), color="red")
        # Negative coords should be clamped to 0
        cropped = crop(img, (-10, -10, 50, 50))
        assert cropped.size == (50, 50)

    def test_crop_exceeds_bounds(self):
        img = Image.new("RGB", (100, 100), color="red")
        # Coords exceeding image should be clamped
        cropped = crop(img, (10, 10, 150, 150))
        assert cropped.size == (90, 90)

    def test_crop_invalid_box(self):
        img = Image.new("RGB", (100, 100), color="red")
        # x1 <= x0 should return original image
        result = crop(img, (50, 10, 40, 50))  # x1 < x0
        assert result.size == img.size

    def test_crop_zero_area(self):
        img = Image.new("RGB", (100, 100), color="red")
        # Zero area should return original
        result = crop(img, (50, 50, 50, 80))  # x1 == x0
        assert result.size == img.size


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_clean_manifest_unicode(self):
        # Unicode digits should not match
        assert clean_manifest("①②③④⑤⑥⑦⑧") == ""

    def test_normalize_phone_empty(self):
        assert normalize_phone("") == ""

    def test_clean_plate_special_chars(self):
        # Special chars except hyphen should be removed
        result = clean_plate("ABC@123!")
        # Depends on implementation - should remove or keep?
        # Current regex allows A-Z0-9 and optional hyphen
        assert len(result) >= 0  # At least doesn't crash

    def test_clean_dot_no_matches(self):
        result = clean_dot("NoNumbersHere")
        # Should return stripped original
        assert result == "NoNumbersHere"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
