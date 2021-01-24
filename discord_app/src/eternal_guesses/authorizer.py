import os
from enum import Enum
from typing import Dict

import discord_interactions
from model.response import Response


class AuthorizationResult(Enum):
    PASS = True
    FAIL = False


def authorize(event: Dict) -> (AuthorizationResult, Response):
    body = event['body'].encode()
    headers = event['headers']
    signature = headers['x-signature-ed25519']
    timestamp = headers['x-signature-timestamp']

    result = discord_interactions.verify_key(body, signature, timestamp, os.environ.get('DISCORD_PUBLIC_KEY'))
    if result:
        return AuthorizationResult.PASS, None
    else:
        return AuthorizationResult.FAIL, Response.unauthorized("could not verify authorization")
