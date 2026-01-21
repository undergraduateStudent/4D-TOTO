from itertools import combinations

class Ticket:
    def __init__(self, game_type, draw_date, numbers, is_system_bet=False):
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
        For TOTO system bets, expand into all possible 6-number combinations.
        For standard bets or 4D, return the original numbers.
        """

        if self.game_type == "TOTO" and self.is_system_bet:
            return list(combinations(self.numbers, 6))

        return [tuple(self.numbers)]



