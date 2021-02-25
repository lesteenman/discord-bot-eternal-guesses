import os
from abc import ABC
from enum import Enum
from typing import Dict

import discord_interactions
from eternal_guesses.model.lambda_response import LambdaResponse


class AuthorizationResult(Enum):
    PASS = True
    FAIL = False


class ApiAuthorizer(ABC):
    def authorize(self, event: Dict) -> (AuthorizationResult, LambdaResponse):
        pass


class ApiAuthorizerImpl(ApiAuthorizer):
    def authorize(self, event: Dict) -> (AuthorizationResult, LambdaResponse):
        body = event['body'].encode()
        headers = event['headers']
        signature = headers['x-signature-ed25519']
        timestamp = headers['x-signature-timestamp']

        result = discord_interactions.verify_key(
            body, signature, timestamp, os.environ.get('DISCORD_PUBLIC_KEY'))
        if result:
            return AuthorizationResult.PASS, None
        else:
            return AuthorizationResult.FAIL, LambdaResponse.unauthorized(
                "could not verify authorization")
