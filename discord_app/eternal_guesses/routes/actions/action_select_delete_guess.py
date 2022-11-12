import re

from eternal_guesses.exceptions import GuessNotFoundError, GameNotFoundError
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.services.guesses_service import GuessesService
from eternal_guesses.util.component_ids import ComponentIds
from eternal_guesses.util.message_provider import MessageProvider


class ActionSelectDeleteGuessRoute(Route):
    def __init__(
        self,
        guesses_service: GuessesService,
        message_provider: MessageProvider,
    ):
        self.message_provider = message_provider
        self.guesses_service = guesses_service

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.component_action is not None and
            event.component_action.component_type == ComponentType.STRING_SELECT and
            event.component_action.component_custom_id.startswith(
                ComponentIds.component_select_delete_guess_prefix
            )
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id

        custom_id = event.component_action.component_custom_id
        game_id = re.search(
            fr"{ComponentIds.component_select_delete_guess_prefix}(.*)",
            custom_id
        ).group(1)

        member_id = int(event.component_action.values[0])

        try:
            await self.guesses_service.delete(
                guild_id=guild_id,
                game_id=game_id,
                member=member_id,
            )

            guess_deleted_message = self.message_provider.guess_deleted()
            return DiscordResponse.ephemeral_channel_message(
                guess_deleted_message
            )
        except GameNotFoundError:
            return DiscordResponse.ephemeral_channel_message(
                content=self.message_provider.error_game_not_found(
                    game_id,
                )
            )
        except GuessNotFoundError:
            return DiscordResponse.ephemeral_channel_message(
                content=self.message_provider.error_guess_not_found(
                    game_id,
                    member_id
                )
            )

        #
        # game = self.games_repository.get(guild_id=guild_id, game_id=game_id)
        #
        # if game is None:
        #     error_game_not_found = self.message_provider.error_game_not_found(
        #         game_id
        #     )
        #     return DiscordResponse.ephemeral_channel_message(
        #         error_game_not_found
        #     )
        #
        # if member_id not in game.guesses:
        #     error_guess_not_found = self.message_provider.error_guess_not_found(
        #         game_id,
        #         member_id
        #     )
        #     return DiscordResponse.ephemeral_channel_message(
        #         error_guess_not_found
        #     )
        #
        # del game.guesses[member_id]
        #
        # self.games_repository.save(game)
        #
        # await self.game_post_manager.update(game)
        #
