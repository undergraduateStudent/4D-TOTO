def get_toto_winning_numbers(draw_date: str):
    if draw_date == "2026-01-20":
        return [1, 5, 12, 23, 34, 45]
    else:
        return None


def get_fourd_winning_numbers(draw_date: str):
    if draw_date == "2026-01-20":
        return {
        "first": "4109",
        "second": "1234",
        "third": "5678",
        "starter": ["0001", "1111"],
        "consolation": ["2222", "3333"]
        }   
    else:
        return None


