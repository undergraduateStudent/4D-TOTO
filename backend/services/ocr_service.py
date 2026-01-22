"""
ocr_service.py

OCR and parsing utilities for extracting lottery ticket information
from an uploaded image.

This file contains helper functions to:
- Extract raw OCR text from an image
- Extract numeric content from OCR text
- Classify game type (TOTO / 4D)
- Validate TOTO numbers and 4D numbers
- Extract the draw date from OCR text (best-effort)
"""

import pytesseract
from PIL import Image
import re
from datetime import datetime

# OPTIONAL: set path explicitly if needed (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(image_path: str) -> str:
    """
    Extract raw text from an image using Tesseract OCR.

    Args:
        image_path (str): Local file path of the uploaded image.

    Returns:
        str: OCR-extracted raw text.
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def extract_numbers_from_text(text: str) -> list[int]:
    """
    Extract all numbers found in the OCR text.

    This function uses a simple regex to find digit sequences. The output
    will include unrelated numbers such as years and dates, which should
    be filtered in later validation.

    Args:
        text (str): OCR raw text.

    Returns:
        list[int]: All extracted numbers as integers.
    """
    numbers = re.findall(r"\d+", text)
    return [int(n) for n in numbers]


def classify_game_type(raw_text: str, numbers: list[int]) -> str:
    """
    Determine game type based on OCR output.

    Current logic:
    - If OCR text contains "4D" or "4-D" -> classify as 4D
    - If OCR text contains "TOTO" -> classify as TOTO
    - Otherwise raise ValueError

    Note:
        There is fallback heuristic logic below, but it is currently unreachable
        because the function raises earlier.

    Args:
        raw_text (str): OCR raw text.
        numbers (list[int]): Extracted numbers from text.

    Returns:
        str: "4D" or "TOTO".

    Raises:
        ValueError: If game type cannot be identified.
    """
    text = raw_text.upper()

    if "4D" in text or "4-D" in text:
        return "4D"

    elif "TOTO" in text:
        return "TOTO"

    else:
        raise ValueError("Unable to determine game type from OCR")


def validate_toto_numbers(numbers: list[int]) -> list[int]:
    """
    Validate and clean OCR-extracted TOTO numbers.

    Steps:
    - Convert all items into integers
    - Keep only numbers in range 1..49
    - Remove duplicates while preserving order
    - Ensure enough numbers exist

    Args:
        numbers (list[int]): OCR extracted numbers.

    Returns:
        list[int]: Cleaned unique TOTO numbers.

    Raises:
        ValueError: If invalid or insufficient numbers were found.
    """
    try:
        numbers = [int(n) for n in numbers]
    except (ValueError, TypeError) as e:
        raise ValueError("Input list contains non-numeric values.") from e

    valid = [n for n in numbers if 1 <= n <= 49]
    unique = list(dict.fromkeys(valid))

    if len(unique) <= 6:
        raise ValueError(
            f"Invalid TOTO ticket: expected exactly 6 numbers, found {len(unique)}"
        )

    return unique


def validate_4d_number(extracted_numbers):
    """
    Validate and reconstruct a 4D ticket number.

    Supported patterns:
    - One complete 4-digit number (e.g. 4109)
    - Four spaced digits (e.g. 4 1 0 9)
    - Split mixed digits (e.g. 410 + 9)

    The function also removes obvious year-like numbers (1900..2100).

    Args:
        extracted_numbers (list[int]): Raw list of extracted numbers.

    Returns:
        str: A 4-digit string (zero-padded if needed).

    Raises:
        ValueError: If a valid 4D number cannot be reconstructed.
    """
    cleaned = [
        n for n in extracted_numbers
        if not (1900 <= n <= 2100)
    ]

    # Case 1: exactly one proper 4-digit number
    four_digit = [n for n in cleaned if 1000 <= n <= 9999]
    if len(four_digit) == 1:
        return str(four_digit[0]).zfill(4)

    # Case 2: spaced digits → 4 single digits
    single_digits = [n for n in cleaned if 0 <= n <= 9]
    if len(single_digits) == 4:
        return "".join(str(d) for d in single_digits)

    # Case 3: mixed split (e.g. 410 + 9)
    short_numbers = [str(n) for n in cleaned if 0 <= n <= 999]
    combined = "".join(short_numbers)
    if len(combined) == 4 and combined.isdigit():
        return combined

    raise ValueError("Invalid 4D ticket format")


def extract_draw_date(raw_text: str) -> str:
    """
    Extract draw date from OCR text using common date patterns.

    Supported formats:
    - YYYY-MM-DD
    - DD/MM/YYYY
    - DD MMM YYYY (e.g. 20 JAN 2026)

    Args:
        raw_text (str): OCR raw text.

    Returns:
        str: ISO date string (YYYY-MM-DD) or "UNKNOWN" if not found.
    """
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{2}\s+[A-Z]{3}\s+\d{4})"
    ]

    for pattern in patterns:
        match = re.search(pattern, raw_text.upper())
        if match:
            date_str = match.group(1)
            try:
                if "-" in date_str:
                    return date_str
                if "/" in date_str:
                    return datetime.strptime(date_str, "%d/%m/%Y").date().isoformat()
                return datetime.strptime(date_str, "%d %b %Y").date().isoformat()
            except ValueError:
                pass

    return "UNKNOWN"
