from eternal_guesses.api.discord_event_handler import DiscordEventHandler
from eternal_guesses.api.router import Router, RouterImpl
from eternal_guesses.authorization.api_authorizer import ApiAuthorizerImpl, ApiAuthorizer
from eternal_guesses.authorization.command_authorizer import CommandAuthorizer, CommandAuthorizerImpl
from eternal_guesses.repositories.configs_repository import ConfigsRepository, ConfigsRepositoryImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl, GamesRepository
from eternal_guesses.routes.add_management_channel import AddManagementChannelRoute
from eternal_guesses.routes.add_management_role import AddManagementRoleRoute
from eternal_guesses.routes.close_game import CloseGameRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.guild_info import GuildInfoRoute
from eternal_guesses.routes.list_games import ListGamesRoute
from eternal_guesses.routes.ping import PingRoute
from eternal_guesses.routes.post import PostRoute
from eternal_guesses.routes.remove_management_channel import RemoveManagementChannelRoute
from eternal_guesses.routes.remove_management_role import RemoveManagementRoleRoute
from eternal_guesses.util.discord_messaging import DiscordMessaging, DiscordMessagingImpl
from eternal_guesses.util.message_provider import MessageProviderImpl, MessageProvider


def discord_event_handler():
    return DiscordEventHandler(
        api_authorizer=_api_authorizer(),
        router=_router(),
    )


def _api_authorizer() -> ApiAuthorizer:
    return ApiAuthorizerImpl()


def _router() -> Router:
    games_repository = _games_repository()
    configs_repository = _configs_repository()
    discord_messaging = _discord_messaging()
    message_provider = _message_provider()
    command_authorizer = _command_authorizer(configs_repository=configs_repository)

    ping_route = _ping_route()
    create_route = _create_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        command_authorizer=command_authorizer,
    )
    guess_route = _guess_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )
    close_game_route = _close_game_route(
        command_authorizer=command_authorizer,
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )
    list_games_route = _list_games_route(
        command_authorizer=command_authorizer,
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )
    post_route = _post_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer
    )
    guild_info_route = _guild_info_route(
        configs_repository=configs_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )
    add_management_channel_route = _add_management_channel_route_route(
        configs_repository=configs_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )
    remove_management_channel_route = _remove_management_channel_route(
        configs_repository=configs_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )
    add_management_role_route = _add_management_role_route(
        configs_repository=configs_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )
    remove_management_role_route = _remove_management_role_route(
        configs_repository=configs_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )

    return RouterImpl(
        ping_route=ping_route,
        post_route=post_route,
        create_route=create_route,
        guess_route=guess_route,
        close_game_route=close_game_route,
        list_games_route=list_games_route,
        guild_info_route=guild_info_route,
        add_management_channel_route=add_management_channel_route,
        remove_management_channel_route=remove_management_channel_route,
        add_management_role_route=add_management_role_route,
        remove_management_role_route=remove_management_role_route,
    )


def _ping_route():
    return PingRoute()


def _post_route(
        games_repository: GamesRepository,
        discord_messaging: DiscordMessaging,
        message_provider: MessageProvider,
        command_authorizer: CommandAuthorizer):
    return PostRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer
    )


def _create_route(games_repository: GamesRepository,
                  discord_messaging: DiscordMessaging,
                  command_authorizer: CommandAuthorizer):
    return CreateRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        command_authorizer=command_authorizer,
    )


def _guess_route(games_repository: GamesRepository,
                 discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider):
    return GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )


def _close_game_route(command_authorizer: CommandAuthorizer,
                      games_repository: GamesRepository,
                      discord_messaging: DiscordMessaging,
                      message_provider: MessageProvider):
    return CloseGameRoute(
        command_authorizer=command_authorizer,
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )


def _list_games_route(command_authorizer: CommandAuthorizer,
                      games_repository: GamesRepository,
                      discord_messaging: DiscordMessaging,
                      message_provider: MessageProvider):
    return ListGamesRoute(
        command_authorizer=command_authorizer,
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )


def _guild_info_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository,
        command_authorizer: CommandAuthorizer,
        discord_messaging: DiscordMessaging):
    return GuildInfoRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer,
        discord_messaging=discord_messaging,
    )


def _add_management_channel_route_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository,
        command_authorizer: CommandAuthorizer,
        discord_messaging: DiscordMessaging):

    return AddManagementChannelRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer,
        discord_messaging=discord_messaging,
    )


def _remove_management_channel_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository,
        command_authorizer: CommandAuthorizer,
        discord_messaging: DiscordMessaging):
    return RemoveManagementChannelRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer,
        discord_messaging=discord_messaging,
    )


def _add_management_role_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository,
        command_authorizer: CommandAuthorizer,
        discord_messaging: DiscordMessaging):
    return AddManagementRoleRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer,
        discord_messaging=discord_messaging,
    )


def _remove_management_role_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository,
        command_authorizer: CommandAuthorizer,
        discord_messaging: DiscordMessaging):
    return RemoveManagementRoleRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer,
        discord_messaging=discord_messaging,
    )


def _games_repository() -> GamesRepository:
    return GamesRepositoryImpl()


def _configs_repository() -> ConfigsRepository:
    return ConfigsRepositoryImpl()


def _discord_messaging() -> DiscordMessaging:
    return DiscordMessagingImpl()


def _message_provider() -> MessageProvider:
    return MessageProviderImpl()


def _command_authorizer(configs_repository: ConfigsRepository) -> CommandAuthorizer:
    return CommandAuthorizerImpl(configs_repository=configs_repository)
