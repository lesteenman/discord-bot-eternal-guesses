from abc import ABC

from loguru import logger

from eternal_guesses.exceptions import BadRouteException, UnknownEventException
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.lambda_response import LambdaResponse


class Router(ABC):
    async def route(self, event: DiscordEvent) -> LambdaResponse:
        pass


class RouterImpl(Router):
    def __init__(self, routes=None):

        self.route_definitions = []
        self.routes = routes or []

    async def route(self, event: DiscordEvent) -> LambdaResponse:
        for route in self.routes:
            if route.matches(event):
                try:
                    discord_response = await route.call(event)
                except Exception as e:
                    logger.error(f"Error occurred in route {route}")
                    raise e

                if discord_response is None:
                    raise BadRouteException(
                        f"Route returned None response: {route}"
                    )

                return LambdaResponse.success(discord_response.json())

        raise UnknownEventException(event)
