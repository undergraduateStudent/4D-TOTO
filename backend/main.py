"""
main.py

FastAPI backend for the Lottery Ticket Checker application.

This API supports:
- Uploading a ticket image for OCR processing and prize checking
- Retrieving saved ticket-check history from SQLite

Main endpoint:
- POST /upload-image-ticket
- GET  /history
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.models.ticket import Ticket
from backend.services.result_checker import ResultChecker
from backend.db.database import init_db, save_ticket, get_all_tickets

from backend.services.ocr_service import (
    extract_text,
    extract_numbers_from_text,
    validate_toto_numbers,
    validate_4d_number,
    classify_game_type,
    extract_draw_date
)

from backend.services.winning_number_service import (
    get_toto_winning_numbers,
    get_fourd_winning_numbers
)

# -------------------------------------------------
# App setup
# -------------------------------------------------
app = FastAPI(title="Lottery Ticket Application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend to call backend locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database at startup
init_db()

# Directory for saving uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_winning_numbers(game_type: str, draw_date: str):
    """
    Fetch winning numbers for a specific game and draw date.

    Args:
        game_type (str): Either "TOTO" or "4D".
        draw_date (str): ISO date string (YYYY-MM-DD) or "UNKNOWN".

    Returns:
        list[int] | dict | None:
            - For TOTO: list of 6 winning numbers
            - For 4D: dictionary of prize categories
            - None: if winning numbers are not available
    """
    if game_type == "TOTO":
        return get_toto_winning_numbers(draw_date)
    elif game_type == "4D":
        return get_fourd_winning_numbers(draw_date)
    return None


@app.post("/upload-image-ticket")
def upload_image_ticket(file: UploadFile = File(...)):
    """
    Upload a lottery ticket image and perform OCR + prize checking.

    Workflow:
    1) Validate file is an image
    2) Save file into uploads/
    3) Run OCR to extract text + numbers
    4) Classify game type (TOTO / 4D)
    5) Extract draw date from text
    6) Validate numbers based on game type
    7) Compare against winning numbers
    8) Save ticket and results into SQLite database
    9) Return result JSON

    Args:
        file (UploadFile): Uploaded ticket image file.

    Returns:
        dict: Ticket info, winning numbers, winner status, and prize results.

    Raises:
        HTTPException:
            - 400 if file is not an image or ticket format is invalid
            - 404 if winning numbers are not available
            - 500 for unexpected errors (OCR/database failures)
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded image locally
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save uploaded image")

    # ---------------- OCR ----------------
    try:
        raw_text = extract_text(file_path)
        extracted_numbers = extract_numbers_from_text(raw_text)

        game_type = classify_game_type(raw_text, extracted_numbers)
        draw_date = extract_draw_date(raw_text)

        if game_type == "TOTO":
            numbers = validate_toto_numbers(extracted_numbers)

        elif game_type == "4D":
            number = validate_4d_number(extracted_numbers)
            numbers = [number]

        else:
            raise ValueError("Unsupported game type")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("OCR ERROR:", e)
        raise HTTPException(status_code=500, detail="OCR processing failed")

    # ---------------- Ticket ----------------
    ticket = Ticket(
        game_type=game_type,
        draw_date=draw_date,
        numbers=numbers,
        is_system_bet=False
    )

    # ---------------- Winning numbers ----------------
    winning_numbers = get_winning_numbers(game_type, draw_date)

    if not winning_numbers:
        raise HTTPException(status_code=404, detail="Winning numbers not available")

    # ---------------- Prize checking ----------------
    if game_type == "TOTO":
        checker = ResultChecker(winning_numbers)
        prize_results = checker.check_combinations(ticket.expand_combinations())
        is_winner = any(count > 0 for count in prize_results.values())

    elif game_type == "4D":
        user_number = numbers[0]
        prize_category = None

        if user_number == winning_numbers["first"]:
            prize_category = "first"
        elif user_number == winning_numbers["second"]:
            prize_category = "second"
        elif user_number == winning_numbers["third"]:
            prize_category = "third"
        elif user_number in winning_numbers["starter"]:
            prize_category = "starter"
        elif user_number in winning_numbers["consolation"]:
            prize_category = "consolation"

        is_winner = prize_category is not None
        prize_results = {"prize_category": prize_category}

    # ---------------- Save ----------------
    try:
        save_ticket(ticket, prize_results, is_winner)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save ticket")

    # ---------------- Response ----------------
    return {
        "game_type": game_type,
        "draw_date": draw_date,
        "extracted_numbers": numbers,
        "winning_numbers": winning_numbers,
        "is_winner": is_winner,
        "prize_results": prize_results
    }


@app.get("/history")
def get_ticket_history():
    """
    Get previously checked tickets from the SQLite database.

    Returns:
        dict: {
            "count": int,
            "tickets": list[dict]
        }
    """
    tickets = get_all_tickets()
    return {"count": len(tickets), "tickets": tickets}

