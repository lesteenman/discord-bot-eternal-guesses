from typing import List

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.guild_config import GuildConfig


def channel_list_game_guesses(game: Game) -> str:
    guess_list = []
    for user_id, guess in game.guesses.items():
        guess_list.append(f"{user_id}: {guess} (<@{user_id}>)")

    if len(guess_list) > 0:
        guesses = "\n".join(guess_list)
    else:
        guesses = "None yet!"

    return f"Actual guesses for {game.game_id}:\n\n{guesses}"


def dm_error_game_not_found(game_id: str) -> str:
    return f"No game found with id {game_id}"


def dm_guess_added(game_id: str, guess: str) -> str:
    return f"Your guess '{guess}' for game '{game_id}' has been registered"


# TODO: Format the roles and channels properly with Discord shizzle
def channel_admin_info(config: GuildConfig) -> str:
    roles = list(f"<@{role}>" for role in config.management_roles)
    channels = list(f"<@{channel}>" for channel in config.management_channels)

    admin_info = f"Eternal-Guess configuration for this server:\n" \
                 f"- management_roles: {roles}\n" \
                 f"- management_channels: {channels}\n" \

    return admin_info


def channel_manage_list_all_games(games: List[Game]) -> str:
    return f"TODO: channel_manage_list_all_games({games})"


def channel_manage_list_open_games(games: List[Game]) -> str:
    return f"TODO: channel_manage_list_open_games({games})"


def channel_manage_list_closed_games(games: List[Game]) -> str:
    return f"TODO: channel_manage_list_open_games({games})"
