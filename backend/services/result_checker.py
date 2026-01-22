"""
result_checker.py

Contains prize-checking logic for TOTO tickets.

Given a set of winning numbers and a list of ticket combinations, this module
counts how many combinations match 3, 4, 5, or 6 numbers.
"""


class ResultChecker:
    """
    Compares ticket number combinations against TOTO winning numbers.

    Attributes:
        winning_numbers (set[int]): The set of winning numbers for the draw.
    """

    def __init__(self, winning_numbers):
        """
        Initialize ResultChecker with TOTO winning numbers.

        Args:
            winning_numbers (list[int] | set[int]): The winning numbers.
        """
        self.winning_numbers = set(winning_numbers)

    def check_combinations(self, combinations):
        """
        Check number combinations and return the number of matches per tier.

        Prize tiers:
        - 3 matches
        - 4 matches
        - 5 matches
        - 6 matches

        Args:
            combinations (list[tuple[int]]): Ticket combinations to compare.

        Returns:
            dict[int, int]: Mapping of {match_count: number_of_combinations}.
        """
        prize_counts = {3: 0, 4: 0, 5: 0, 6: 0}

        for combo in combinations:
            matched_numbers = set(combo) & self.winning_numbers
            match_count = len(matched_numbers)

            if match_count >= 3:
                prize_counts[match_count] += 1

        return prize_counts


