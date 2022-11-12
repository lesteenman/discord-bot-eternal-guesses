from abc import ABC

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse


class Route(ABC):
    async def call(self, event: DiscordEvent) -> DiscordResponse:
        raise NotImplementedError()

    # TODO: Merge RouteDefinition with Route.
    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        raise NotImplementedError()
