import pprint
from typing import Dict

from loguru import logger

from eternal_guesses.util import injector

discord_event_handler = None


def handle_lambda(event, context) -> Dict:
    global discord_event_handler

    if discord_event_handler is None:
        logger.debug("initializing a new DiscordEventHandler.")
        discord_event_handler = injector.discord_event_handler()

    # if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"body: {pprint.pformat(event['body'])}")
    logger.debug(f"headers:{pprint.pformat(event['headers'])}")
    logger.debug(f"context:{pprint.pformat(context)}")

    return discord_event_handler.handle(event)
