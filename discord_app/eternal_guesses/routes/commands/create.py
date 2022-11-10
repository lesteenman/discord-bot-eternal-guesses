from datetime import datetime

from loguru import logger

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_component import DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util import id_generator
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class CreateRoute(Route):
    def __init__(self,
                 games_repository: GamesRepository,
                 discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider):
        self.discord_messaging = discord_messaging
        self.games_repository = games_repository
        self.message_provider = message_provider

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = event.command.options.get('game-id')
        title = event.command.options.get('title')
        description = event.command.options.get('description')
        min_guess = event.command.options.get('min')
        max_guess = event.command.options.get('max')

        if all([o is None for o in [game_id, title, description, min_guess, max_guess]]):
            return self.create_modal()

        if game_id is None:
            game_id = self._generate_game_id(guild_id)
        else:
            existing_game = self.games_repository.get(guild_id, game_id)
            if existing_game is not None:
                message = self.message_provider.duplicate_game_id(game_id)

                return DiscordResponse.ephemeral_channel_message(message)

        game = Game(
            guild_id=guild_id,
            game_id=game_id,
            title=title,
            description=description,
            min_guess=min_guess,
            max_guess=max_guess,
            created_by=event.member.user_id,
            create_datetime=datetime.now(),
            close_datetime=None,
            closed=False,
        )
        self.games_repository.save(game)

        game_created_message = self.message_provider.game_created(game)
        return DiscordResponse.ephemeral_channel_message(game_created_message)

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

    def create_modal(self):
        return DiscordResponse.modal(
            custom_id=f"modal_create_game",
            title="Create new game",
            components=[
                DiscordComponent.text_input(
                    custom_id=f"modal_create_game_id",
                    label="Game Identifier",
                ),
                DiscordComponent.text_input(
                    custom_id=f"modal_create_game_title",
                    label="Game Title",
                ),
                DiscordComponent.text_input(
                    custom_id=f"modal_create_game_description",
                    label="Description",
                    paragraph=True,
                ),
                DiscordComponent.text_input(
                    custom_id=f"modal_create_game_min_value",
                    label="Min guess (optional)",
                    required=False,
                ),
                DiscordComponent.text_input(
                    custom_id=f"modal_create_game_max_value",
                    label="Max guess (optional)",
                    required=False,
                ),
            ]
        )
