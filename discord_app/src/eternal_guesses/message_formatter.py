from typing import List

from eternal_guesses.model.data.game import Game
from model.data.guild_config import GuildConfig


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


# TODO: Format the roles and channels properly with Discord shizzle
def channel_admin_info(config: GuildConfig) -> str:
    admin_info = f"Eternal-Guess configuration for this guild:\n" \
                 f"- management_roles: {config.management_roles}\n" \
                 f"- management_channels: {config.management_channels}\n" \

    return admin_info


def channel_manage_list_all_games(games: List[Game]) -> str:
    return f"TODO: channel_manage_list_all_games({games})"


def channel_manage_list_open_games(games: List[Game]) -> str:
    return f"TODO: channel_manage_list_open_games({games})"


def channel_manage_list_closed_games(games: List[Game]) -> str:
    return f"TODO: channel_manage_list_open_games({games})"
