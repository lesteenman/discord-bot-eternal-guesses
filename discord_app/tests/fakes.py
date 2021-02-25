from typing import List, Optional

from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_member import DiscordMember
from eternal_guesses.repositories.games_repository import GamesRepository


# class FakeApiAuthorizer(ApiAuthorizer):
#     def __init__(self, passes: bool):
#         self.passes = passes
#
#     def authorize(self, event: Dict) -> (AuthorizationResult, LambdaResponse):
#         if self.passes:
#             return AuthorizationResult.PASS, None
#         else:
#             return AuthorizationResult.FAIL, LambdaResponse()


class FakeCommandAuthorizer(CommandAuthorizer):
    def __init__(self, passes: bool):
        self.passes = passes

    async def authorize_management_call(self, event: DiscordEvent):
        if self.passes is False:
            raise DiscordEventDisallowedError("Disallowed")


class FakeDiscordMessaging(DiscordMessaging):
    def __init__(self):
        self.updated_channel_messages = []
        self.sent_dms = []
        self.sent_channel_messages = []
        self.created_channel_message_id = 0

    async def create_channel_message(self, channel_id: int, text: str) -> int:
        self.sent_channel_messages.append({'channel_id': channel_id, 'text': text})
        return self.created_channel_message_id

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        self.updated_channel_messages.append({'channel_id': channel_id, 'message_id': message_id, 'text': text})

    async def send_dm(self, member: DiscordMember, message: str):
        self.sent_dms.append({'member': member, 'text': message})


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
