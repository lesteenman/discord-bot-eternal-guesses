import json
import logging
import os
from typing import Dict

import response
import discord_interactions
from handlers import ping

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def handle_lambda(event, context):
    log.debug(f"request: {json.dumps(event)}")
    log.info(f"body:\n{event['body']}'")
    log.info(f"headers:\n{event['headers']}'")

    if verify_request(event):
        return handle_request(event)
    else:
        return response.unauthorized()


def handle_request(event) -> Dict:
    body = json.loads(event['body'])
    if body['type'] == discord_interactions.InteractionType.PING:
        log.info("handling 'ping'")
        return response.success(ping.call(body))

    if body['type'] == discord_interactions.InteractionType.APPLICATION_COMMAND:
        log.warning('Application command received, not yet implemented')
        return {}


def verify_request(event) -> bool:
    body = event['body'].encode()
    headers = event['headers']
    signature = headers['x-signature-ed25519']
    timestamp = headers['x-signature-timestamp']
    return discord_interactions.verify_key(body, signature, timestamp, os.environ.get('DISCORD_PUBLIC_KEY'))
