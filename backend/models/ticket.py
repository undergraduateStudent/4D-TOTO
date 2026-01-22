"""
ticket.py

Defines the Ticket model used in the lottery ticket checker system.

A Ticket contains:
- game type (TOTO or 4D)
- draw date
- extracted numbers
- whether it is a system bet (for TOTO)

For TOTO system bets, this file also provides logic to expand a ticket into
all possible 6-number combinations.
"""

from itertools import combinations


class Ticket:
    """
    Represents a lottery ticket submitted by a user.

    Attributes:
        game_type (str): "TOTO" or "4D"
        draw_date (str): ISO date string (YYYY-MM-DD) or "UNKNOWN"
        numbers (list[int] | list[str]): Ticket numbers extracted from OCR
        is_system_bet (bool): Whether this is a TOTO system-bet ticket
    """

    def __init__(self, game_type, draw_date, numbers, is_system_bet=False):
        """
        Create a Ticket instance and validate its content.

        Args:
            game_type (str): Either "TOTO" or "4D"
            draw_date (str): Draw date (ISO format or UNKNOWN)
            numbers (list): Extracted ticket numbers
            is_system_bet (bool): Enables system-bet combination expansion for TOTO

        Raises:
            ValueError: If ticket data is invalid or unsupported.
        """
        if game_type not in ["TOTO", "4D"]:
            raise ValueError("Invalid game type")

        if game_type == "TOTO":
            if len(numbers) <= 6:
                raise ValueError("TOTO requires at least 6 numbers")
            if len(set(numbers)) != len(numbers):
                raise ValueError("Duplicate numbers not allowed")

        if game_type == "4D":
            if len(numbers) != 1:
                raise ValueError("4D requires 4 numbers")

        self.game_type = game_type
        self.draw_date = draw_date
        self.numbers = numbers
        self.is_system_bet = is_system_bet

    def expand_combinations(self):
        """
        Expand ticket numbers into combinations.

        - If game type is TOTO and is_system_bet is True:
          return all possible 6-number combinations.
        - Otherwise (standard bet or 4D):
          return one "combination" containing the original numbers.

        Returns:
            list[tuple]: A list of number tuples representing combinations.
        """
        if self.game_type == "TOTO" and self.is_system_bet:
            return list(combinations(self.numbers, 6))

        return [tuple(self.numbers)]




