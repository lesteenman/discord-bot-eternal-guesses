import asyncio
import logging
from typing import Dict

import discord_interactions
import interact
from model.response import Response
from routes import ping

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


async def handle_application_command(body: Dict):
    log.warning('Application command received, not yet implemented')

    member = body['member']
    log.debug(f"member:\n{member}")

    user = member['user']
    log.debug(f"user:\n{user}")

    await interact.send_dm(user['id'])

    return {
        "type": 4,
        "data": {
            "tts": False,
            "content": "Congrats on sending your command!",
            "embeds": [],
            "allowed_mentions": []
        }
    }


def route(request_body: Dict) -> Response:
    if request_body['type'] == discord_interactions.InteractionType.PING:
        log.info("handling 'ping'")
        response_body = ping.call(request_body)
        return Response.success(response_body)

    if request_body['type'] == discord_interactions.InteractionType.APPLICATION_COMMAND:
        response_body = asyncio.get_event_loop() \
            .run_until_complete(handle_application_command(request_body))
        return Response.success(response_body)
