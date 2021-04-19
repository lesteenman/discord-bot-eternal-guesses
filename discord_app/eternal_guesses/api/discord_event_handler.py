import asyncio
import json
from typing import Dict

from eternal_guesses.authorization.api_authorizer import ApiAuthorizer, AuthorizationResult
from eternal_guesses.model.discord import discord_event
from eternal_guesses.api.router import Router


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
