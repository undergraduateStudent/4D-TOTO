"""
winning_number_service.py

Provides winning number data for lottery draws.

Currently, this module contains hardcoded (mock) winning results to make the
project stable for demonstration and testing.

In the future, this can be replaced with:
- live web scraping
- an official API (if available)
- admin input stored in database
"""


def get_toto_winning_numbers(draw_date: str):
    """
    Return TOTO winning numbers for the requested draw date.

    Args:
        draw_date (str): Draw date in ISO format (YYYY-MM-DD).

    Returns:
        list[int] | None: List of 6 winning numbers, or None if not available.
    """
    if draw_date == "2026-01-20":
        return [1, 5, 12, 23, 34, 45]
    return None


def get_fourd_winning_numbers(draw_date: str):
    """
    Return 4D winning numbers for the requested draw date.

    Args:
        draw_date (str): Draw date in ISO format (YYYY-MM-DD).

    Returns:
        dict | None:
            Dictionary containing first/second/third prizes and starter/consolation,
            or None if not available.
    """
    if draw_date == "2026-01-20":
        return {
            "first": "4109",
            "second": "1234",
            "third": "5678",
            "starter": ["0001", "1111"],
            "consolation": ["2222", "3333"]
        }
    return None



