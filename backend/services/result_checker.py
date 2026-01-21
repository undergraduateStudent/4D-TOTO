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

