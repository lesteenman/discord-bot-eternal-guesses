import random


def game_id():
    hex_id = '%08x' % random.randrange(16 ** 8)
    return f"game-{hex_id}"
