import asyncio
import json
import logging
from typing import Dict

from eternal_guesses import api_authorizer
from eternal_guesses import router
from eternal_guesses.model import discord_event

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def handle_lambda(event, context) -> Dict:
    log.debug(f"request: {json.dumps(event)}")
    log.info(f"body:\n{event['body']}'")
    log.info(f"headers:\n{event['headers']}'")

    result, response = api_authorizer.authorize(event)
    if result == api_authorizer.AuthorizationResult.PASS:
        body_json = json.loads(event['body'])
        event = discord_event.from_event(body_json)

        response = asyncio.get_event_loop() \
            .run_until_complete(router.route(event))

    return response.json()
