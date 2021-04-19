from loguru import logger
from datetime import datetime

from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util import id_generator
from eternal_guesses.util.discord_messaging import DiscordMessaging


class CreateRoute(Route):
    def __init__(self,
                 games_repository: GamesRepository,
                 discord_messaging: DiscordMessaging,
                 command_authorizer: CommandAuthorizer):
        self.discord_messaging = discord_messaging
        self.games_repository = games_repository
        self.command_authorizer = command_authorizer

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_management_call(event)

        guild_id = event.guild_id
        game_id = event.command.options.get('game-id')
        title = event.command.options.get('title')
        description = event.command.options.get('description')

        if game_id is None:
            game_id = self._generate_game_id(guild_id)
        else:
            existing_game = self.games_repository.get(guild_id, game_id)
            if existing_game is not None:
                await self.discord_messaging.send_channel_message(
                    text=f"Game id '{game_id}' already exists.",
                    channel_id=event.channel_id,
                )

                return DiscordResponse.acknowledge()

        game = Game(
            guild_id=guild_id,
            game_id=game_id,
            title=title,
            description=description,
            created_by=event.member.user_id,
            create_datetime=datetime.now(),
            close_datetime=None,
            closed=False
        )
        self.games_repository.save(game)

        await self.discord_messaging.send_channel_message(
            text=f"Game created with id '{game_id}'.",
            channel_id=event.channel_id,
        )

        return DiscordResponse.acknowledge()

    def _generate_game_id(self, guild_id: int, attempt: int = 0):
        if attempt >= 10:
            raise Exception(
                f"Could not generate a unique game_id after {attempt} attempts.")

        game_id = id_generator.game_id()
        existing_game = self.games_repository.get(guild_id, game_id)
        logger.info(f"existing game for game_id {game_id} = {existing_game}")
        if existing_game is None:
            return game_id
        else:
            return self._generate_game_id(guild_id, attempt + 1)
