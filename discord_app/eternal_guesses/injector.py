from eternal_guesses.api_authorizer import ApiAuthorizerImpl
from eternal_guesses.discord_event_handler import DiscordEventHandler
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.router import Router, RouterImpl
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.routes.ping import PingRoute


def _manage_route(games_repository):
    return ManageRoute(games_repository=games_repository)


def _create_route(games_repository):
    return CreateRoute(games_repository=games_repository)


def _guess_route(games_repository):
    return GuessRoute(games_repository=games_repository)


def _ping_route():
    return PingRoute()


def _admin_route():
    return AdminRoute()


def _api_authorizer():
    return ApiAuthorizerImpl()


def _games_repository():
    return GamesRepository()


def _router() -> Router:
    games_repository = _games_repository()

    manage_route = _manage_route(games_repository=games_repository)
    create_route = _create_route(games_repository=games_repository)
    guess_route = _guess_route(games_repository=games_repository)
    ping_route = _ping_route()
    admin_route = _admin_route()

    return RouterImpl(manage_route=manage_route, create_route=create_route, guess_route=guess_route,
                      ping_route=ping_route, admin_route=admin_route)


def discord_event_handler():
    return DiscordEventHandler(router=_router(), api_authorizer=_api_authorizer())
