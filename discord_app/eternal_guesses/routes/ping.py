import logging

from eternal_guesses.model.discord_response import DiscordResponse

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class PingRoute:
    async def call(self) -> DiscordResponse:
        return DiscordResponse.pong()
