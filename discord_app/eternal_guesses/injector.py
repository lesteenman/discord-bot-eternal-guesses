from eternal_guesses.authorization.api_authorizer import ApiAuthorizerImpl, ApiAuthorizer
from eternal_guesses.authorization.command_authorizer import CommandAuthorizer, CommandAuthorizerImpl
from eternal_guesses.discord_event_handler import DiscordEventHandler
from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.repositories.configs_repository import ConfigsRepository, ConfigsRepositoryImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl, GamesRepository
from eternal_guesses.router import Router, RouterImpl
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.routes.ping import PingRoute
from eternal_guesses.util.message_provider import MessageProviderImpl, MessageProvider


def _manage_route(games_repository: GamesRepository, discord_messaging: DiscordMessaging,
                  message_provider: MessageProvider, command_authorizer: CommandAuthorizer):
    return ManageRoute(games_repository=games_repository, discord_messaging=discord_messaging,
                       message_provider=message_provider, command_authorizer=command_authorizer)


def _create_route(games_repository: GamesRepository):
    return CreateRoute(games_repository=games_repository)


def _guess_route(games_repository: GamesRepository, discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider):
    return GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )


def _ping_route():
    return PingRoute()


def _admin_route(message_provider: MessageProvider, configs_repository: ConfigsRepository,
                 command_authorizer: CommandAuthorizer):
    return AdminRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer
    )


def _api_authorizer() -> ApiAuthorizer:
    return ApiAuthorizerImpl()


def _games_repository() -> GamesRepository:
    return GamesRepositoryImpl()


def _configs_repository() -> ConfigsRepository:
    return ConfigsRepositoryImpl()


def _discord_messaging() -> DiscordMessaging:
    return DiscordMessaging()


def _message_provider() -> MessageProvider:
    return MessageProviderImpl()


def _command_authorizer(configs_repository: ConfigsRepository) -> CommandAuthorizer:
    return CommandAuthorizerImpl(configs_repository=configs_repository)


def _router() -> Router:
    games_repository = _games_repository()
    configs_repository = _configs_repository()
    discord_messaging = _discord_messaging()
    message_provider = _message_provider()
    command_authorizer = _command_authorizer(configs_repository=configs_repository)

    ping_route = _ping_route()
    create_route = _create_route(games_repository=games_repository)
    admin_route = _admin_route(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer
    )
    guess_route = _guess_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )
    manage_route = _manage_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer
    )

    return RouterImpl(
        manage_route=manage_route,
        create_route=create_route,
        guess_route=guess_route,
        ping_route=ping_route,
        admin_route=admin_route
    )


def discord_event_handler():
    return DiscordEventHandler(router=_router(), api_authorizer=_api_authorizer())
