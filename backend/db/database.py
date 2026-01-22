"""
database.py

SQLite database utilities for storing ticket checks.

This module handles:
- database initialization
- saving checked tickets
- retrieving ticket history

Data is stored in tickets.db using a single table "tickets".
"""

import sqlite3
import json
from datetime import datetime

DB_NAME = "tickets.db"


def get_connection():
    """
    Create and return a SQLite connection.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    return sqlite3.connect(
        DB_NAME,
        timeout=5,
        check_same_thread=False
    )


def init_db():
    """
    Initialize the SQLite database if it does not exist.

    Creates table `tickets` with fields for:
    - ticket information
    - prize checking result
    - winner status
    - created timestamp
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type TEXT,
            draw_date TEXT,
            numbers TEXT,
            is_system_bet INTEGER,
            prize_results TEXT,
            is_winner INTEGER,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_ticket(ticket, prize_results, is_winner):
    """
    Save a checked ticket record into the database.

    Args:
        ticket (Ticket): Ticket object containing extracted ticket details.
        prize_results (dict): Prize checking output results.
        is_winner (bool): Whether ticket won any prize.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (
            game_type,
            draw_date,
            numbers,
            is_system_bet,
            prize_results,
            is_winner,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket.game_type,
        ticket.draw_date,
        json.dumps(ticket.numbers),
        int(ticket.is_system_bet),
        json.dumps(prize_results),
        int(is_winner),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_all_tickets():
    """
    Retrieve all saved ticket records from the database.

    Returns:
        list[dict]: List of tickets ordered by created_at descending.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            game_type,
            draw_date,
            numbers,
            is_system_bet,
            prize_results,
            is_winner,
            created_at
        FROM tickets
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    tickets = []

    for row in rows:
        tickets.append({
            "id": row[0],
            "game_type": row[1],
            "draw_date": row[2],
            "numbers": json.loads(row[3]),
            "is_system_bet": bool(row[4]),
            "prize_results": json.loads(row[5]),
            "is_winner": bool(row[6]),
            "created_at": row[7]
        })

    return tickets
