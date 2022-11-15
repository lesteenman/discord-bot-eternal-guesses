from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route


class PingRoute(Route):
    async def call(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.pong()

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.command is not None and
            event.command.command_name == 'ping'
        )
