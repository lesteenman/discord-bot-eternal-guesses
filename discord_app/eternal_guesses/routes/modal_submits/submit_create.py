from datetime import datetime

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.custom_id_generator import CustomIdGenerator
from eternal_guesses.util.message_provider import MessageProvider


class SubmitCreateRoute(Route):
    def __init__(self, games_repository: GamesRepository, message_provider: MessageProvider):
        self.games_repository = games_repository
        self.message_provider = message_provider

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = self.input_value(event, CustomIdGenerator.submit_create_game_id)
        title = event.command.options.get('title')
        description = event.command.options.get('description')
        min_guess = event.command.options.get('min')
        max_guess = event.command.options.get('max')

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

    def input_value(self, event, submit_create_game_id):
        for c in event.modal_submit.input_value:
            pass

