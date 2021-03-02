from eternal_guesses.model.discord_response import DiscordResponse


class PingRoute:
    async def call(self) -> DiscordResponse:
        return DiscordResponse.pong()
