import re

from eternal_guesses.model.discord.discord_component import ComponentType, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds
from eternal_guesses.util.message_provider import MessageProvider


class ActionSelectEditGuessRoute(Route):
    def __init__(
        self,
        # guesses_service: GuessesService,
        message_provider: MessageProvider,
    ):

        # self.guesses_service = guesses_service
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        action = event.component_action
        if action is None:
            return False

        if action.component_type != ComponentType.STRING_SELECT:
            return False

        custom_id = action.component_custom_id
        return custom_id.startswith(
            ComponentIds.component_select_edit_guess_prefix
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        custom_id = event.component_action.component_custom_id
        game_id = re.search(
            fr"{ComponentIds.component_select_edit_guess_prefix}(.*)",
            custom_id
        ).group(1)

        member_id = int(event.component_action.values[0])

        return DiscordResponse.modal(
            custom_id=ComponentIds.edit_guess_modal_id(game_id, member_id),
            title="Edit Guess",
            components=[
                DiscordComponent.text_input(
                    custom_id=ComponentIds.edit_guess_modal_input_id,
                    label="Enter new guess",
                )
            ]
        )

        # try:
        #     self.guesses_service.edit(
        #         guild_id=guild_id,
        #         game_id=game_id,
        #         member=member_id,
        #         guess=new_guess,
        #     )
        # except GameNotFoundError:
        #     return DiscordResponse.ephemeral_channel_message(
        #         content=self.message_provider.error_game_not_found(
        #             game_id
        #         )
        #     )
        #
        # #
        # # game = self.games_repository.get(guild_id=guild_id, game_id=game_id)
        # #
        # # if game is None:
        # #     error_game_not_found = self.message_provider.error_game_not_found(
        # #         game_id
        # #     )
        # #     return DiscordResponse.ephemeral_channel_message(
        # #         error_game_not_found
        # #     )
        # #
        # # if member_id not in game.guesses:
        # #     error_guess_not_found = self.message_provider.error_guess_not_found(
        # #         game_id,
        # #         member_id
        # #     )
        # #     return DiscordResponse.ephemeral_channel_message(
        # #         error_guess_not_found
        # #     )
        # #
        # # del game.guesses[member_id]
        # #
        # # self.games_repository.save(game)
        # #
        # # await self.game_post_manager.update(game)
        # #
        # #
        # # try:
        # #     guess_deleted_message = self.message_provider.guess_deleted()
        # #     return DiscordResponse.ephemeral_channel_message(guess_deleted_message)
        # # except GuessNotFoundError:
        # #     guess_not_found_error = self.message_provider.error_guess_not_found(
        # #         game_id,
        # #         member
        # #     )
        # #     return DiscordResponse.ephemeral_channel_message(
        # #         guess_not_found_error
        # #     )
