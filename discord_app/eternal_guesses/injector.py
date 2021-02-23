from eternal_guesses.api_authorizer import ApiAuthorizerImpl
from eternal_guesses.discord_event_handler import DiscordEventHandler
from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from eternal_guesses.router import Router, RouterImpl
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.routes.ping import PingRoute


def _manage_route(games_repository: GamesRepositoryImpl, discord_messaging: DiscordMessaging,
                  configs_repository: ConfigsRepository):
    return ManageRoute(games_repository=games_repository, discord_messaging=discord_messaging,
                       configs_repository=configs_repository)


def _create_route(games_repository: GamesRepositoryImpl):
    return CreateRoute(games_repository=games_repository)


def _guess_route(games_repository: GamesRepositoryImpl, discord_messaging: DiscordMessaging):
    return GuessRoute(games_repository=games_repository, discord_messaging=discord_messaging)


def _ping_route():
    return PingRoute()


def _admin_route():
    return AdminRoute()


def _api_authorizer():
    return ApiAuthorizerImpl()


def _games_repository():
    return GamesRepositoryImpl()


def _configs_repository():
    return ConfigsRepository()


def _discord_messaging():
    return DiscordMessaging()


def _router() -> Router:
    games_repository = _games_repository()
    configs_repository = _configs_repository()
    discord_messaging = _discord_messaging()

    manage_route = _manage_route(games_repository=games_repository, discord_messaging=discord_messaging,
                                 configs_repository=configs_repository)
    create_route = _create_route(games_repository=games_repository)
    guess_route = _guess_route(games_repository=games_repository, discord_messaging=discord_messaging)
    ping_route = _ping_route()
    admin_route = _admin_route()

    return RouterImpl(manage_route=manage_route, create_route=create_route, guess_route=guess_route,
                      ping_route=ping_route, admin_route=admin_route)


def discord_event_handler():
    return DiscordEventHandler(router=_router(), api_authorizer=_api_authorizer())
