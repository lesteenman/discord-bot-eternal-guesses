import typing
from abc import ABC

from loguru import logger

from eternal_guesses.api.route_definition import RouteDefinition
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.error.discord_event_disallowed_error import DiscordEventDisallowedError
from eternal_guesses.model.error.unkonwn_event_exception import UnknownEventException
from eternal_guesses.model.lambda_response import LambdaResponse
from eternal_guesses.routes.route import Route


class Router(ABC):
    async def route(self, event: DiscordEvent) -> LambdaResponse:
        pass


class RouterImpl(Router):
    def __init__(self,
                 close_game_route: Route,
                 list_games_route: Route,
                 post_route: Route,
                 create_route: Route,
                 guess_route: Route,
                 ping_route: Route,
                 guild_info_route: Route,
                 add_management_channel_route: Route,
                 remove_management_channel_route: Route,
                 add_management_role_route: Route,
                 remove_management_role_route: Route):
        self.list_games_route = list_games_route
        self.close_game_route = close_game_route
        self.post_route = post_route
        self.create_route = create_route
        self.guess_route = guess_route
        self.ping_route = ping_route
        self.guild_info_route = guild_info_route
        self.add_management_channel_route = add_management_channel_route
        self.remove_management_channel_route = remove_management_channel_route
        self.add_management_role_route = add_management_role_route
        self.remove_management_role_route = remove_management_role_route

        self.routes = []
        self._register_routes()

    def _register_routes(self):
        self._register(RouteDefinition(self.ping_route, 'ping'))
        self._register(RouteDefinition(self.guess_route, 'guess'))
        self._register(RouteDefinition(self.post_route, 'manage', 'post', permission='manage'))
        self._register(RouteDefinition(self.close_game_route, 'manage', 'close', permission='manage'))
        self._register(RouteDefinition(self.list_games_route, 'manage', 'list-games', permission='manage'))
        self._register(RouteDefinition(self.create_route, 'create', permission='manage'))
        self._register(RouteDefinition(self.guild_info_route, 'admin', 'info', permission='admin'))
        self._register(RouteDefinition(self.add_management_channel_route, 'admin', 'add-management-channel',
                                       permission='admin'))
        self._register(RouteDefinition(self.remove_management_channel_route, 'admin', 'remove-management-channel',
                                       permission='admin'))
        self._register(RouteDefinition(self.add_management_role_route, 'admin', 'add-management-role',
                                       permission='admin'))
        self._register(RouteDefinition(self.remove_management_role_route, 'admin', 'remove-management-role',
                                       permission='admin'))

    def _register(self, definition: RouteDefinition):
        self.routes.append(definition)

    async def route(self, event: DiscordEvent) -> LambdaResponse:
        route = self.find_matching_route(event)

        if route is None:
            raise UnknownEventException(event)

        try:
            discord_response = await route.handle(event)
            return LambdaResponse.success(discord_response.json())
        except DiscordEventDisallowedError as e:
            logger.warning(f"disallowed call detected: {e}")
            return LambdaResponse.unauthorized(str(e))

    def find_matching_route(self, event: DiscordEvent) -> typing.Optional[RouteDefinition]:
        for route in self.routes:
            if route.matches(event.command):
                return route

        return None
