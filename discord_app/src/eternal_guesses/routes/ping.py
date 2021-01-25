import logging

from eternal_guesses.model.discord_response import DiscordResponse

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def call() -> DiscordResponse:
    return DiscordResponse.pong()
