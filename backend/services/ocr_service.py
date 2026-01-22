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
    Extract raw text from an image using OCR.
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def extract_numbers_from_text(text: str) -> list[int]:

     # Remove draw date line
    #cleaned_text = re.sub(r"Draw Date:.*", "", text)

    """
    Extract all numbers found in OCR text.
    """
    numbers = re.findall(r"\d+", text)
    return [int(n) for n in numbers]


def classify_game_type(raw_text: str, numbers: list[int]) -> str:
    """
    Best-effort classification of game type based on OCR text and extracted numbers.
    """
    text = raw_text.upper()

    if "4D" in text or "4-D" in text:
        return "4D"

    elif "TOTO" in text:
        return "TOTO"
    
    else:
        raise ValueError("Unable to determine game type from OCR")
        

    # Heuristic fallback
    if len(numbers) == 4 and all(0 <= n <= 9 for n in numbers):
        return "4D"

    elif len(numbers) >= 6:
        return "TOTO"

    #if len(numbers) <
    else:
        raise ValueError("Unable to determine game type from OCR")


def validate_toto_numbers(numbers: list[int]) -> list[int]:
    """
    Validate and clean OCR-extracted TOTO numbers.
    """

    try:
        numbers = [int(n) for n in numbers]
    except (ValueError, TypeError) as e:
        raise ValueError("Input list contains non-numeric values.") from e
        
    # Remove invalid ranges
    valid = [n for n in numbers if 1 <= n <= 49]

    # Remove duplicates while preserving order
    unique = list(dict.fromkeys(valid))

    if len(unique) <= 6:
        raise ValueError(f"Invalid TOTO ticket: expected exactly 6 numbers, found {len(unique)}")

    return unique #[:6]

def validate_4d_number(extracted_numbers):
    """
    Robust 4D validation:
    - Accepts 4-digit grouped numbers (4109)
    - Accepts spaced digits (4 1 0 9)
    - Accepts mixed (410 9)
    - Ignores draw date / year values
    """

    # Remove obvious years
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
    Best-effort extraction of draw date from OCR text.
    Returns ISO date string or 'UNKNOWN'.
    """
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",       # 2026-01-20
        r"(\d{2}/\d{2}/\d{4})",       # 20/01/2026
        r"(\d{2}\s+[A-Z]{3}\s+\d{4})" # 20 JAN 2026
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