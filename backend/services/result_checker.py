"""
result_checker.py

Contains prize-checking logic for TOTO tickets.

Given a set of winning numbers and a list of ticket combinations, this module
counts how many combinations match 3, 4, 5, or 6 numbers.
"""


class ResultChecker:
    def __init__(self, winning_numbers):
        self.winning_numbers = set(winning_numbers)

    def check_combinations(self, combinations):
        """
        Check all combinations and return prize tier counts.
        """
        prize_counts = {
            3: 0,
            4: 0,
            5: 0,
            6: 0
        }

        for combo in combinations:
            matched_numbers = set(combo) & self.winning_numbers
            match_count = len(matched_numbers)

            if match_count >= 3:
                prize_counts[match_count] += 1

        return prize_counts
