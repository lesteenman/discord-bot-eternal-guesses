from model.data.game import Game


def channel_list_game_guesses(game: Game) -> str:
    return f"Game {game.game_id} guesses: {game.guesses}"


def dm_error_game_not_found(game_id: str) -> str:
    return f"No game found with id {game_id}"


def dm_guess_added(game_id: str, guess: str) -> str:
    return f"Your guess '{guess}' for game '{game_id}' has been registered"