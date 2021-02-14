import logging
import pprint
from typing import Dict

from eternal_guesses import injector

log = logging.getLogger(__name__)


discord_event_handler = None


def handle_lambda(event, context) -> Dict:
    global discord_event_handler

    if discord_event_handler is None:
        log.debug("initializing a new DiscordEventHandler.")
        discord_event_handler = injector.discord_event_handler()

    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"body: {pprint.pformat(event['body'])}")
        log.debug(f"headers:{pprint.pformat(event['headers'])}")
        log.debug(f"context:{pprint.pformat(context)}")

    return discord_event_handler.handle(event)
