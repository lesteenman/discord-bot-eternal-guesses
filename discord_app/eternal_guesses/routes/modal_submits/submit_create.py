import re
from datetime import datetime

from loguru import logger

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.app.message_provider import MessageProvider


class SubmitCreateRoute(Route):
    def __init__(
        self,
        games_repository: GamesRepository,
        message_provider: MessageProvider
    ):
        self.games_repository = games_repository
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        submit = event.modal_submit
        return (
            submit is not None and
            submit.modal_custom_id == ComponentIds.submit_create_modal_id
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id

        inputs = event.modal_submit.inputs

        game_id = self.normalize(
            inputs[ComponentIds.submit_create_input_game_id]
        )

        logger.info(f"user {event.member.user_id} creating game {game_id}")

        title = inputs[ComponentIds.submit_create_input_title]
        description = inputs[ComponentIds.submit_create_input_description]

        min_guess = inputs[ComponentIds.submit_create_input_min_value]
        if min_guess or min_guess == 0:
            min_guess = int(min_guess)

        max_guess = inputs[ComponentIds.submit_create_input_max_value]
        if max_guess or max_guess == 0:
            max_guess = int(max_guess)

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
        return DiscordResponse.ephemeral_channel_message(
            content=game_created_message,
            action_rows=[
                ActionRow(
                    components=[
                        DiscordComponent.button(
                            custom_id=ComponentIds.component_button_post_game_id(game_id),
                            label="Post to channel",
                        )
                    ]
                )
            ]
        )

    def normalize(self, game_id):
        game_id = re.sub(r"[^a-z0-9-]", "-", game_id.lower())
        game_id = re.sub(r"-+", "-", game_id)
        return game_id
