from abc import ABC
from typing import List

import discord
from discord import ButtonStyle

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.util.custom_id_generator import CustomIdGenerator


class MessageProvider(ABC):
    def game_post_view(self, game: Game) -> discord.ui.View:
        raise NotImplementedError()

    def game_post_embed(self, game: Game) -> discord.Embed:
        raise NotImplementedError()

    def error_game_not_found(self, game_id: str) -> str:
        raise NotImplementedError()

    def error_guess_not_found(self, game_id: str, member_id: int) -> str:
        raise NotImplementedError()

    def guess_added(self, game_id: str, guess: str) -> str:
        raise NotImplementedError()

    def channel_admin_info(self, guild_config: GuildConfig) -> str:
        raise NotImplementedError()

    def channel_manage_list_all_games(self, games: List[Game]) -> str:
        raise NotImplementedError()

    def channel_manage_list_open_games(self, games: List[Game]) -> str:
        raise NotImplementedError()

    def channel_manage_list_closed_games(self, games: List[Game]) -> str:
        raise NotImplementedError()

    def error_guess_on_closed_game(self, game_id):
        raise NotImplementedError()

    def error_duplicate_guess(self, game_id):
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

    def disallowed_management_call(self, command) -> str:
        raise NotImplementedError()

    def disallowed_admin_call(self, command) -> str:
        raise NotImplementedError()

    def game_closed(self, game) -> str:
        raise NotImplementedError()

    def game_created(self, game) -> str:
        raise NotImplementedError()

    def duplicate_game_id(self, game_id) -> str:
        raise NotImplementedError()

    def game_post_created_message(self) -> str:
        raise NotImplementedError()

    def bot_missing_access(self) -> str:
        raise NotImplementedError()

    def guess_edited(self) -> str:
        raise NotImplementedError()

    def guess_deleted(self) -> str:
        raise NotImplementedError()

    def invalid_guess(self, game: Game) -> str:
        raise NotImplementedError()

    def modal_input_label_guess_value(self, game: Game) -> str:
        raise NotImplementedError()

    def modal_title_place_guess(self, game: Game) -> str:
        raise NotImplementedError()


class MessageProviderImpl(MessageProvider):
    def game_post_view(self, game: Game) -> discord.ui.View:
        view = discord.ui.View()

        make_guess_button = discord.ui.Button(
            style=ButtonStyle.secondary,
            label="Guess!",
            custom_id=CustomIdGenerator.trigger_guess_modal_action(game.game_id),
        )
        view.add_item(make_guess_button)

        return view

    def game_post_embed(self, game: Game) -> discord.Embed:
        if game.title:
            title = game.title
        else:
            title = game.game_id

        description = ""
        if game.description:
            description += f"{game.description}\n\n"

        description += "Guesses:\n\n"

        guess_list = []
        for user_id, guess in _sorted_guesses(game):
            guess_list.append(f"<@{user_id}>: {guess.guess}")

        if len(guess_list) > 0:
            guesses = "\n".join(guess_list)
        else:
            guesses = "None yet!"
        description = f"{description}{guesses}"

        embed = discord.Embed(title=title, description=description, color=0x723EEA)

        if game.closed:
            embed.set_footer(text="Game closed.")
        # else:
        #     embed.add_field(name="Place your guess", value=f"/guess game-id:{game.game_id} guess:1234")

        return embed

    def error_game_not_found(self, game_id: str) -> str:
        return f"No game found with id {game_id}."

    def error_guess_not_found(self, game_id: str, member_id: str) -> str:
        return f"No guess found by <@{member_id}> found for game {game_id}."

    def guess_added(self, game_id: str, guess: str) -> str:
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

    def error_guess_on_closed_game(self, game_id):
        return f"This game ({game_id}) has already been closed."

    def error_duplicate_guess(self, game_id):
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

    def disallowed_management_call(self, command: DiscordCommand) -> str:
        if command.subcommand_name:
            command_name = f"/eternal-guess {command.command_name} {command.subcommand_name}"
        else:
            command_name = f"/eternal-guess {command.command_name}"

        return f"You are not allowed to use '{command_name}' from this channel."

    def disallowed_admin_call(self, command: DiscordCommand) -> str:
        if command.subcommand_name:
            command_name = f"/eternal-guess {command.command_name} {command.subcommand_name}"
        else:
            command_name = f"/eternal-guess {command.command_name}"

        return f"You are not allowed to use '{command_name}'."

    def game_closed(self, game) -> str:
        return f"Game {game.game_id} has been closed for new guesses."

    def duplicate_game_id(self, game_id) -> str:
        return f"Another game with id '{game_id}' already exists."

    def game_post_created_message(self) -> str:
        return "Game post created. It will be automatically updated if new guesses are placed."

    def game_created(self, game) -> str:
        return f"Game {game.game_id} created."

    def bot_missing_access(self) -> str:
        return "The bot is missing permissions to perform this command. Please inform a server admin."

    def guess_edited(self) -> str:
        return "The guess has been edited."

    def guess_deleted(self) -> str:
        return "The guess has been deleted."

    def invalid_guess(self, game: Game) -> str:
        if game.min_guess is not None and game.max_guess is not None:
            return f"The guess must be a number between {game.min_guess} and {game.max_guess}"
        elif game.min_guess is not None:
            return f"The guess must be a number higher than {game.min_guess}"
        elif game.max_guess is not None:
            return f"The guess must be a number lower than {game.max_guess}"

        raise NotImplementedError()

    def modal_input_label_guess_value(self, game: Game) -> str:
        if game.min_guess is not None and game.max_guess is not None:
            return f"Your guess ({game.min_guess} - {game.max_guess})"
        elif game.min_guess is not None:
            return f"Your guess (at least {game.min_guess})"
        elif game.max_guess is not None:
            return f"Your guess (at most {game.max_guess})"

        return "Your guess"

    def modal_title_place_guess(self, game: Game):
        return f"Guess for '{game.game_id}'"


def _sorted_guesses(game):
    if game.is_numeric():
        return sorted(game.guesses.items(), key=lambda i: int(i[1].guess))
    else:
        return sorted(game.guesses.items(), key=lambda i: i[1].guess)
