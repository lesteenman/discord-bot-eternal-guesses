import asyncio
import json
import logging
import pprint
from typing import Dict

from eternal_guesses import api_authorizer
from eternal_guesses import router
from eternal_guesses.model import discord_event

log = logging.getLogger(__name__)


def handle_lambda(event, context) -> Dict:
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"body: {pprint.pformat(event['body'])}")
        log.debug(f"headers:{pprint.pformat(event['headers'])}")
        log.debug(f"context:{pprint.pformat(context)}")

    result, response = api_authorizer.authorize(event)
    if result == api_authorizer.AuthorizationResult.PASS:
        body_json = json.loads(event['body'])
        event = discord_event.from_event(body_json)

        response = asyncio.get_event_loop() \
            .run_until_complete(router.route(event))

    return response.json()
