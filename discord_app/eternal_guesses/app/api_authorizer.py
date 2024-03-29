from abc import ABC
from enum import Enum
from typing import Dict

from loguru import logger
from nacl.signing import VerifyKey

from eternal_guesses.model.lambda_response import LambdaResponse
from eternal_guesses.app import app_config


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

        result = self.verify_key(
            body, signature, timestamp, app_config.discord_public_key()
        )
        if result:
            return AuthorizationResult.PASS, None
        else:
            return AuthorizationResult.FAIL, LambdaResponse.unauthorized(
                "could not verify authorization"
            )

    def verify_key(self, body, signature, timestamp, public_key):
        message = timestamp.encode() + body
        try:
            vk = VerifyKey(bytes.fromhex(public_key))
            vk.verify(message, bytes.fromhex(signature))
            return True
        except Exception as ex:
            logger.exception(ex)
        return False
