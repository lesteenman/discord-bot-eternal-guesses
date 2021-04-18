from abc import ABC
from typing import List

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.guild_config import GuildConfig


class MessageProvider(ABC):
    # def game_post_embed(self, game: Game) -> discord.Embed:
    #     raise NotImplementedError()

    def game_managed_channel_message(self, game: Game) -> str:
        raise NotImplementedError()

    def manage_error_game_not_found(self, game_id: str) -> str:
        raise NotImplementedError()

    def dm_guess_added(self, game_id: str, guess: str) -> str:
        raise NotImplementedError()

    def channel_admin_info(self, guild_config: GuildConfig) -> str:
        raise NotImplementedError()

    def channel_manage_list_all_games(self, games: List[Game]) -> str:
        raise NotImplementedError()

    def channel_manage_list_open_games(self, games: List[Game]) -> str:
        raise NotImplementedError()

    def channel_manage_list_closed_games(self, games: List[Game]) -> str:
        raise NotImplementedError()

    def dm_error_guess_on_closed_game(self, game_id):
        raise NotImplementedError()

    def dm_error_duplicate_guess(self, game_id):
        raise NotImplementedError()

    def error_duplicate_management_channel(self, channel):
        raise NotImplementedError()

    def admin_removed_management_role(self, role):
        raise NotImplementedError()

    def remove_invalid_management_role(self, role):
        raise NotImplementedError()

    def added_management_role(self, role):
        raise NotImplementedError()

    def add_duplicate_management_role(self, role):
        raise NotImplementedError()

    def removed_management_channel(self, channel):
        raise NotImplementedError()

    def remove_invalid_management_channel(self, channel):
        raise NotImplementedError()

    def added_management_channel(self, channel):
        raise NotImplementedError()


class MessageProviderImpl(MessageProvider):
    def game_managed_channel_message(self, game: Game) -> str:
        message = ""
        if game.title:
            message = f"**{game.title}**\n\n"

        if game.description:
            message += f"{game.description}\n\n"

        message += "Guesses:\n\n"

        guess_list = []
        for user_id, guess in sorted(game.guesses.items(), key=lambda i: i[1].guess):
            guess_list.append(f"<@{user_id}>: {guess.guess}")

        if len(guess_list) > 0:
            guesses = "\n".join(guess_list)
        else:
            guesses = "None yet!"
        message = f"{message}{guesses}"

        if game.closed:
            message = f"{message}\n\n" \
                      f"This game has been closed for new guesses."
        else:
            message = f"{message}\n\n" \
                      f"To add your own guess, copy this template and post it in the chat:" \
                        f"`/guess game-id: {game.game_id} guess:`"

        return message

    def manage_error_game_not_found(self, game_id: str) -> str:
        return f"No game found with id {game_id}."

    def dm_guess_added(self, game_id: str, guess: str) -> str:
        return f"Your guess '{guess}' for game '{game_id}' has been registered."

    def channel_admin_info(self, guild_config: GuildConfig) -> str:
        roles = ", ".join(f"<@{role}>" for role in guild_config.management_roles)
        channels = ", ".join(f"<#{channel}>" for channel in guild_config.management_channels)

        admin_info = f"Eternal-Guess configuration for this server:\n" \
                     f"- management_roles: {roles}\n" \
                     f"- management_channels: {channels}\n"
        return admin_info

    def channel_manage_list_all_games(self, games: List[Game]) -> str:
        lines = []
        for game in games:
            line = f"- {game.game_id}"
            if game.closed:
                line = f"{line} (closed)"

            lines.append(line)

        return "All games:\n" + "\n".join(sorted(lines))

    def channel_manage_list_open_games(self, games: List[Game]) -> str:
        lines = []
        for game in games:
            lines.append(f"- {game.game_id}")

        return "All open games:\n" + "\n".join(sorted(lines))

    def channel_manage_list_closed_games(self, games: List[Game]) -> str:
        lines = []
        for game in games:
            lines.append(f"- {game.game_id}")

        return "All closed games:\n" + "\n".join(sorted(lines))

    def dm_error_guess_on_closed_game(self, game_id):
        return f"The game '{game_id}' you placed a guess for has already been closed."

    def dm_error_duplicate_guess(self, game_id):
        return f"You have already placed a guess for game '{game_id}'"

    def error_duplicate_management_channel(self, channel):
        return f"<#{channel}> is already a management channel."

    def admin_removed_management_role(self, role):
        return f"Removed management role: <@&{role}>"

    def remove_invalid_management_role(self, role):
        return f"role <@&{role}> is not a management role."

    def added_management_role(self, role):
        return f"Added new management role: <@&{role}>"

    def add_duplicate_management_role(self, role):
        return f"Role <@&{role}> is already a management role."

    def removed_management_channel(self, channel):
        return f"Removed management channel: <#{channel}>"

    def remove_invalid_management_channel(self, channel):
        return f"Channel <#{channel}> was not a management channel."

    def added_management_channel(self, channel):
        return f"Added new management channel: <#{channel}>"
