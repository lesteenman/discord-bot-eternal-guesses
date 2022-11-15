import re

from loguru import logger

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.services.guesses_service import GuessesService
from eternal_guesses.app.component_ids import ComponentIds


class SubmitEditGuessRoute(Route):
    def __init__(
        self,
        guesses_service: GuessesService
    ):
        self.guesses_service = guesses_service

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        if event.modal_submit is None:
            return False

        modal_id = event.modal_submit.modal_custom_id
        return (
            event.modal_submit is not None and
            modal_id.startswith(ComponentIds.edit_guess_modal_prefix)
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        modal_submit = event.modal_submit
        matches = re.search(
            ComponentIds.edit_guess_modal_regex,
            modal_submit.modal_custom_id
        )
        game_id = matches.group(1)
        member_id = int(matches.group(2))
        new_guess = modal_submit.inputs[ComponentIds.edit_guess_modal_input_id]

        logger.info(f"guild_id={event.guild_id}, user {event.member.user_id} "
                    f"editing guess by member {member_id} in "
                    f"game {game_id} to guess '{new_guess}'")

        await self.guesses_service.edit(
            guild_id=event.guild_id,
            game_id=game_id,
            member=member_id,
            guess=new_guess,
        )

        return DiscordResponse.ephemeral_channel_message(
            content="Guess succesfully edited."
        )
