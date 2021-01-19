import asyncio
import json
import logging
import os
from typing import Dict, Awaitable

import interact
import response
import discord_interactions
from handlers import ping

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def handle_lambda(event, context) -> Dict:
    log.debug(f"request: {json.dumps(event)}")
    log.info(f"body:\n{event['body']}'")
    log.info(f"headers:\n{event['headers']}'")

    if verify_request(event):
        return handle_request(event)
    else:
        return response.unauthorized()


async def handle_application_command(body: Dict):
    log.warning('Application command received, not yet implemented')

    member = body['member']
    log.debug(f"member:\n{member}")

    user = member['user']
    log.debug(f"user:\n{user}")

    await interact.send_dm(user['id'])

    return response.success({
        "type": 4,
        "data": {
            "tts": False,
            "content": "Congrats on sending your command!",
            "embeds": [],
            "allowed_mentions": []
        }
    })


def handle_request(event) -> Dict:
    body = json.loads(event['body'])
    if body['type'] == discord_interactions.InteractionType.PING:
        log.info("handling 'ping'")
        return response.success(ping.call(body))

    if body['type'] == discord_interactions.InteractionType.APPLICATION_COMMAND:
        asyncio.get_event_loop()\
            .run_until_complete(handle_application_command(body))


def verify_request(event) -> bool:
    body = event['body'].encode()
    headers = event['headers']
    signature = headers['x-signature-ed25519']
    timestamp = headers['x-signature-timestamp']
    return discord_interactions.verify_key(body, signature, timestamp, os.environ.get('DISCORD_PUBLIC_KEY'))
