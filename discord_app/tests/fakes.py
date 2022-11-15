from typing import List, Optional

import discord

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.app.discord_messaging import DiscordMessaging
from eternal_guesses.app.message_provider import MessageProvider


class FakeNotFound(discord.NotFound):
    def __init__(self):
        pass


class FakeDiscordMessaging(DiscordMessaging):
    def __init__(self):
        self.updated_channel_messages = []
        self.sent_dms = []
        self.sent_channel_messages = []
        self.sent_temp_messages = []
        self.created_channel_message_id = 0
        self.deleted_messages = []

    async def send_channel_message(
        self,
        channel_id: int,
        text: str = None,
        embed: discord.Embed = None,
        view: discord.ui.View = None
    ) -> int:
        obj = {
            'channel_id': channel_id
        }

        if text is not None:
            obj['text'] = text

        if embed is not None:
            obj['embed'] = embed

        if view is not None:
            obj['view'] = view

        self.sent_channel_messages.append(obj)

        return self.created_channel_message_id

    async def update_channel_message(
        self, channel_id: int, message_id: int, text: str = None,
        embed: discord.Embed = None, view: discord.ui.View = None
    ):
        if message_id in self.deleted_messages:
            raise FakeNotFound()
        else:
            obj = {
                'channel_id': channel_id,
                'message_id': message_id,
            }

            if text is not None:
                obj['text'] = text
            if embed is not None:
                obj['embed'] = embed
            if view is not None:
                obj['view'] = view

            self.updated_channel_messages.append(obj)

    async def send_dm(self, member: DiscordMember, text: str):
        self.sent_dms.append(
            {
                'member': member,
                'text': text
            }
        )

    def raise_404_on_update_of_message(self, message_id):
        self.deleted_messages.append(message_id)


class FakeGamesRepository(GamesRepository):
    def __init__(self, games: List[Game] = None):
        if games is None:
            games = []

        self.games = games

    def get(self, guild_id: int, game_id: str) -> Optional[Game]:
        for game in self.games:
            if game.guild_id == guild_id and game.game_id == game_id:
                return game

        return None

    def save(self, game: Game):
        for g in self.games:
            if g.game_id == game.game_id:
                self.games.remove(g)

        self.games.append(game)

    def get_all(self, guild_id: int) -> List[Game]:
        return self.games


class FakeMessageProvider(MessageProvider):
    def error_guess_not_found(self, game_id: str, member_id: int) -> str:
        pass

    def bot_missing_access(self) -> str:
        pass

    def guess_edited(self) -> str:
        pass

    def guess_deleted(self) -> str:
        pass

    def invalid_guess(self, game: Game) -> str:
        pass

    def modal_input_label_guess_value(self, game: Game) -> str:
        pass

    def modal_title_place_guess(self, game: Game) -> str:
        pass

    def game_post_view(self, game: Game) -> discord.ui.View:
        pass

    def game_post_embed(self, game: Game) -> discord.Embed:
        pass

    def game_managed_channel_message(self, game: Game) -> str:
        pass

    def error_game_not_found(self, game_id: str) -> str:
        pass

    def guess_added(self, game_id: str, guess: str) -> str:
        pass

    def channel_manage_list_all_games(self, games: List[Game]) -> str:
        pass

    def channel_manage_list_open_games(self, games: List[Game]) -> str:
        pass

    def channel_manage_list_closed_games(self, games: List[Game]) -> str:
        pass

    def error_guess_on_closed_game(self, game_id):
        pass

    def error_duplicate_guess(self, game_id):
        pass

    def error_duplicate_management_channel(self, channel):
        pass

    def admin_removed_management_role(self, role):
        pass

    def remove_invalid_management_role(self, role):
        pass

    def added_management_role(self, role):
        pass

    def add_duplicate_management_role(self, role):
        pass

    def removed_management_channel(self, channel):
        pass

    def remove_invalid_management_channel(self, channel):
        pass

    def added_management_channel(self, channel):
        pass

    def __init__(self):
        self.message = None
        self.expected_config = None

    def expect_channel_admin_info_call(
        self,
        expected_config: GuildConfig,
        message: str
    ):
        self.expected_config = expected_config
        self.message = message

    def channel_admin_info(self, guild_config: GuildConfig) -> str:
        if guild_config == self.expected_config:
            return self.message

    def disallowed_management_call(self, command) -> str:
        pass

    def disallowed_admin_call(self, command) -> str:
        pass

    def game_closed(self, game) -> str:
        pass

    def game_created(self, game) -> str:
        pass

    def duplicate_game_id(self, game_id) -> str:
        pass

    def game_post_created_message(self) -> str:
        pass
