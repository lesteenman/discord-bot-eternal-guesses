import boto3

from eternal_guesses.api.discord_event_handler import DiscordEventHandler
from eternal_guesses.api.route_handler import RouteHandlerImpl
from eternal_guesses.api.router import Router, RouterImpl
from eternal_guesses.authorization.api_authorizer import ApiAuthorizerImpl, \
    ApiAuthorizer
from eternal_guesses.authorization.command_authorizer import CommandAuthorizer, \
    CommandAuthorizerImpl
from eternal_guesses.repositories.configs_repository import ConfigsRepository, \
    ConfigsRepositoryImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl, \
    GamesRepository
from eternal_guesses.routes.actions.action_game_guess import \
    ActionGameGuessRoute
from eternal_guesses.routes.actions.action_manage_game_delete_guess import \
    ActionManageGameDeleteGuessRoute
from eternal_guesses.routes.actions.action_manage_game_edit_guess import \
    ActionManageGameEditGuessRoute
from eternal_guesses.routes.actions.action_manage_game_post import \
    ActionManageGamePostRoute
from eternal_guesses.routes.commands.add_management_channel import \
    AddManagementChannelRoute
from eternal_guesses.routes.commands.add_management_role import \
    AddManagementRoleRoute
from eternal_guesses.routes.commands.close_game import CloseGameRoute
from eternal_guesses.routes.commands.create import CreateRoute
from eternal_guesses.routes.commands.delete_guess import DeleteGuessRoute
from eternal_guesses.routes.commands.edit_guess import EditGuessRoute
from eternal_guesses.routes.commands.guess import GuessRoute
from eternal_guesses.routes.commands.guild_info import GuildInfoRoute
from eternal_guesses.routes.commands.list_games import ListGamesRoute
from eternal_guesses.routes.commands.manage_game import ManageGameRoute
from eternal_guesses.routes.commands.message_with_buttons_test import \
    MessageWithButtonsRoute
from eternal_guesses.routes.commands.ping import PingRoute
from eternal_guesses.routes.commands.post import PostRoute
from eternal_guesses.routes.commands.remove_management_channel import \
    RemoveManagementChannelRoute
from eternal_guesses.routes.commands.remove_management_role import \
    RemoveManagementRoleRoute
from eternal_guesses.routes.modal_submits.modal_test import ModalTestRoute
from eternal_guesses.routes.modal_submits.submit_guess import SubmitGuessRoute
from eternal_guesses.util import app_config
from eternal_guesses.util.discord_messaging import DiscordMessaging, \
    DiscordMessagingImpl
from eternal_guesses.util.game_post_manager import GamePostManager, \
    GamePostManagerImpl
from eternal_guesses.util.message_provider import MessageProviderImpl, \
    MessageProvider


def discord_event_handler():
    return DiscordEventHandler(
        api_authorizer=_api_authorizer(),
        router=_router(),
    )


def _api_authorizer() -> ApiAuthorizer:
    return ApiAuthorizerImpl()


def _router() -> Router:
    eternal_guesses_table = _eternal_guesses_table()
    games_repository = _games_repository(eternal_guesses_table)
    configs_repository = _configs_repository(eternal_guesses_table)

    discord_messaging = _discord_messaging()
    message_provider = _message_provider()

    command_authorizer = _command_authorizer(configs_repository=configs_repository)

    game_post_manager = GamePostManagerImpl(
        games_repository=games_repository,
        message_provider=message_provider,
        discord_messaging=discord_messaging,
    )

    route_handler = _route_handler(
        command_authorizer=command_authorizer,
        message_provider=message_provider,
    )

    ping_route = _ping_route()
    create_route = _create_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )
    guess_route = _guess_route(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
        message_provider=message_provider
    )
    close_game_route = _close_game_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )
    list_games_route = _list_games_route(
        games_repository=games_repository,
        message_provider=message_provider
    )
    post_route = _post_route(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )
    guild_info_route = _guild_info_route(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )
    add_management_channel_route = _add_management_channel_route_route(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )
    remove_management_channel_route = _remove_management_channel_route(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )
    add_management_role_route = _add_management_role_route(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )
    remove_management_role_route = _remove_management_role_route(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )
    edit_guess_route = _edit_guess_route(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )
    delete_guess_route = _delete_guess_route(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )
    trigger_guess_modal_route = _action_game_guess_route(
        message_provider=message_provider,
        games_repository=games_repository,
    )
    action_post_game_route = _action_manage_game_post_route()
    action_trigger_edit_guess_route = _action_manage_game_edit_guess_route(
        message_provider=message_provider,
        games_repository=games_repository,
    )
    action_trigger_delete_guess_route = _action_manage_game_edit_guess_route(
        message_provider=message_provider,
        games_repository=games_repository,
    )
    submit_guess_route = _submit_guess_route(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
        message_provider=message_provider,
    )
    modal_test_route = _modal_test_route(
        game_post_manager=game_post_manager
    )
    message_with_buttons_route = _message_with_buttons_route(
        game_post_manager=game_post_manager
    )
    manage_game_route = _manage_game_route(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    return RouterImpl(
        route_handler=route_handler,
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
        edit_guess_route=edit_guess_route,
        delete_guess_route=delete_guess_route,
        trigger_guess_modal_route=trigger_guess_modal_route,
        submit_guess_route=submit_guess_route,
        modal_test_route=modal_test_route,
        message_with_buttons_route=message_with_buttons_route,
        manage_game_route=manage_game_route,
        action_post_game_route=action_post_game_route,
        action_trigger_edit_guess_route=action_trigger_edit_guess_route,
        action_trigger_delete_guess_route=action_trigger_delete_guess_route,
    )


def _route_handler(command_authorizer: CommandAuthorizer,
                   message_provider: MessageProvider):
    return RouteHandlerImpl(
        command_authorizer=command_authorizer,
        message_provider=message_provider,
    )


def _ping_route():
    return PingRoute()


def _post_route(
        games_repository: GamesRepository,
        discord_messaging: DiscordMessaging,
        message_provider: MessageProvider):
    return PostRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )


def _create_route(games_repository: GamesRepository,
                  discord_messaging: DiscordMessaging,
                  message_provider: MessageProvider,):
    return CreateRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )


def _guess_route(games_repository: GamesRepository,
                 game_post_manager: GamePostManager,
                 message_provider: MessageProvider):
    return GuessRoute(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )


def _close_game_route(games_repository: GamesRepository,
                      discord_messaging: DiscordMessaging,
                      message_provider: MessageProvider):
    return CloseGameRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )


def _list_games_route(games_repository: GamesRepository,
                      message_provider: MessageProvider):
    return ListGamesRoute(
        games_repository=games_repository,
        message_provider=message_provider,
    )


def _guild_info_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository):
    return GuildInfoRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )


def _add_management_channel_route_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository):

    return AddManagementChannelRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )


def _remove_management_channel_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository):
    return RemoveManagementChannelRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )


def _add_management_role_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository):
    return AddManagementRoleRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )


def _remove_management_role_route(
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository):
    return RemoveManagementRoleRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )


def _edit_guess_route(
        games_repository: GamesRepository,
        message_provider: MessageProvider,
        game_post_manager: GamePostManager,
):
    return EditGuessRoute(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )


def _delete_guess_route(
        games_repository: GamesRepository,
        message_provider: MessageProvider,
        game_post_manager: GamePostManager,
):
    return DeleteGuessRoute(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )


def _submit_guess_route(
    games_repository: GamesRepository,
    game_post_manager: GamePostManager,
    message_provider: MessageProvider
):
    return SubmitGuessRoute(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
        message_provider=message_provider,
    )


def _action_game_guess_route(message_provider, games_repository):
    return ActionGameGuessRoute(
        message_provider=message_provider,
        games_repository=games_repository,
    )


def _manage_game_route(message_provider, games_repository):
    return ManageGameRoute(
        message_provider=message_provider,
        games_repository=games_repository,
    )


def _action_manage_game_post_route():
    return ActionManageGamePostRoute()


def _action_manage_game_delete_guess_route(message_provider, games_repository):
    return ActionManageGameDeleteGuessRoute(
        message_provider=message_provider,
        games_repository=games_repository,
    )


def _action_manage_game_edit_guess_route(message_provider, games_repository):
    return ActionManageGameEditGuessRoute(
        message_provider=message_provider,
        games_repository=games_repository,
    )


def _modal_test_route(game_post_manager):
    return ModalTestRoute()


def _message_with_buttons_route(game_post_manager):
    return MessageWithButtonsRoute()


def _eternal_guesses_table():
    dynamodb = boto3.resource(
        service_name='dynamodb',
        endpoint_url=app_config.aws_endpoint_url(),
    )
    return dynamodb.Table(app_config.dynamodb_table_name())


def _games_repository(eternal_guesses_table) -> GamesRepository:
    return GamesRepositoryImpl(eternal_guesses_table)


def _configs_repository(eternal_guesses_table) -> ConfigsRepository:
    return ConfigsRepositoryImpl(eternal_guesses_table)


def _discord_messaging() -> DiscordMessaging:
    return DiscordMessagingImpl()


def _message_provider() -> MessageProvider:
    return MessageProviderImpl()


def _command_authorizer(configs_repository: ConfigsRepository) -> CommandAuthorizer:
    return CommandAuthorizerImpl(configs_repository=configs_repository)
