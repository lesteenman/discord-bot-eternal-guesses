import asyncio
import json
import logging
import pprint
from typing import Dict

from eternal_guesses import injector
from eternal_guesses.api_authorizer import ApiAuthorizer, AuthorizationResult
from eternal_guesses.model import discord_event
from eternal_guesses.router import Router

log = logging.getLogger(__name__)


class DiscordEventHandler:
    def __init__(self, router: Router, api_authorizer: ApiAuthorizer):
        self.router = router
        self.api_authorizer = api_authorizer

    def handle(self, event) -> Dict:
        result, response = self.api_authorizer.authorize(event)
        if result == AuthorizationResult.PASS:
            body_json = json.loads(event['body'])
            event = discord_event.from_event(body_json)

            response = asyncio.get_event_loop() \
                .run_until_complete(self.router.route(event))

        return response.json()


discord_event_handler = None


def handle_lambda(event, context) -> Dict:
    global discord_event_handler

    if discord_event_handler is None:
        log.debug("initializing a new DiscordEventHandler.")
        discord_event_handler = DiscordEventHandler(router=injector.router(),
                                                    api_authorizer=injector.api_authorizer())

    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"body: {pprint.pformat(event['body'])}")
        log.debug(f"headers:{pprint.pformat(event['headers'])}")
        log.debug(f"context:{pprint.pformat(context)}")

    return discord_event_handler.handle(event)
