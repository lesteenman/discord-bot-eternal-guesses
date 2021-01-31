from eternal_guesses.model.data.game import Game


def channel_list_game_guesses(game: Game) -> str:
    guess_list = []
    for user_id, guess in game.guesses.items():
        guess_list.append(f"{user_id}: {guess}")

    guesses = "\n".join(guess_list)
    return f"Actual guesses for {game.game_id}:\n\n{guesses}"


def dm_error_game_not_found(game_id: str) -> str:
    return f"No game found with id {game_id}"


def dm_guess_added(game_id: str, guess: str) -> str:
    return f"Your guess '{guess}' for game '{game_id}' has been registered"
