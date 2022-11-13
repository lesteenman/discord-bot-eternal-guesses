import boto3

from eternal_guesses.app import app_config
from eternal_guesses.app.api_authorizer import ApiAuthorizerImpl, \
    ApiAuthorizer
from eternal_guesses.app.discord_event_handler import DiscordEventHandler
from eternal_guesses.app.discord_messaging import DiscordMessagingImpl
from eternal_guesses.app.game_post_manager import GamePostManagerImpl
from eternal_guesses.app.message_provider import MessageProviderImpl
from eternal_guesses.app.router import Router, RouterImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from eternal_guesses.routes.actions.action_edit_game_routes import \
    ActionEditGameTitleRoute, ActionEditGameMinGuessRoute, \
    ActionEditGameMaxGuessRoute, ActionEditGameDescriptionRoute
from eternal_guesses.routes.actions.action_game_guess import \
    ActionGameGuessRoute
from eternal_guesses.routes.actions.action_manage_game_close import \
    ActionManageGameCloseRoute
from eternal_guesses.routes.actions.action_manage_game_delete_guess import \
    ActionManageGameDeleteGuessRoute
from eternal_guesses.routes.actions.action_manage_game_edit import \
    ActionManageGameEditRoute
from eternal_guesses.routes.actions.action_manage_game_edit_guess import \
    ActionManageGameEditGuessRoute
from eternal_guesses.routes.actions.action_manage_game_post import \
    ActionManageGamePostRoute
from eternal_guesses.routes.actions.action_manage_game_reopen import \
    ActionManageGameReopenRoute
from eternal_guesses.routes.actions.action_select_delete_guess import \
    ActionSelectDeleteGuessRoute
from eternal_guesses.routes.actions.action_select_edit_guess import \
    ActionSelectEditGuessRoute
from eternal_guesses.routes.actions.action_select_game_to_manage import \
    ActionSelectGameToManageRoute
from eternal_guesses.routes.actions.action_select_post_game import \
    ActionSelectPostGameRoute
from eternal_guesses.routes.commands.create import CreateRoute
from eternal_guesses.routes.commands.list_games import ListGamesRoute
from eternal_guesses.routes.commands.ping import PingRoute
from eternal_guesses.routes.modal_submits.submit_create import SubmitCreateRoute
from eternal_guesses.routes.modal_submits.submit_edit_game_routes import \
    SubmitEditGameTitleRoute, SubmitEditGameDescriptionRoute, \
    SubmitEditGameMaxGuessRoute, SubmitEditGameMinGuessRoute
from eternal_guesses.routes.modal_submits.submit_edit_guess import \
    SubmitEditGuessRoute
from eternal_guesses.routes.modal_submits.submit_guess import SubmitGuessRoute
from eternal_guesses.services.games_service import GamesService
from eternal_guesses.services.guesses_service import GuessesService


def discord_event_handler():
    return DiscordEventHandler(
        api_authorizer=_api_authorizer(),
        router=_router(),
    )


def _api_authorizer() -> ApiAuthorizer:
    return ApiAuthorizerImpl()


def _router() -> Router:
    dynamodb = boto3.resource(
        service_name='dynamodb',
        endpoint_url=app_config.aws_endpoint_url(),
    )

    eternal_guesses_table = dynamodb.Table(app_config.dynamodb_table_name())

    games_repository = GamesRepositoryImpl(eternal_guesses_table)

    discord_messaging = DiscordMessagingImpl()
    message_provider = MessageProviderImpl()

    game_post_manager = GamePostManagerImpl(
        games_repository=games_repository,
        message_provider=message_provider,
        discord_messaging=discord_messaging,
    )

    games_service = GamesService(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    guesses_service = GuessesService(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    return RouterImpl(
        routes=[
            PingRoute(),
            ActionGameGuessRoute(
                message_provider=message_provider,
                games_repository=games_repository,
            ),
            ActionManageGamePostRoute(),
            ActionManageGameCloseRoute(
                games_service=games_service,
                games_repository=games_repository,
            ),
            ActionManageGameReopenRoute(
                games_service=games_service,
                games_repository=games_repository,
            ),
            ActionSelectDeleteGuessRoute(
                guesses_service=guesses_service,
                message_provider=message_provider,
            ),
            ActionSelectEditGuessRoute(
                message_provider=message_provider,
            ),
            ActionSelectGameToManageRoute(
                games_repository=games_repository,
            ),
            ActionSelectPostGameRoute(
                message_provider=message_provider,
                games_service=games_service,
            ),
            ActionManageGameEditRoute(
                games_repository=games_repository,
            ),
            ActionEditGameTitleRoute(),
            ActionEditGameMinGuessRoute(),
            ActionEditGameMaxGuessRoute(),
            ActionEditGameDescriptionRoute(),
            SubmitEditGameTitleRoute(
                games_service=games_service,
            ),
            SubmitEditGameMinGuessRoute(
                games_service=games_service,
            ),
            SubmitEditGameMaxGuessRoute(
                games_service=games_service,
            ),
            SubmitEditGameDescriptionRoute(
                games_service=games_service,
            ),
            SubmitGuessRoute(
                games_repository=games_repository,
                game_post_manager=game_post_manager,
                message_provider=message_provider,
            ),
            SubmitCreateRoute(
                games_repository=games_repository,
                message_provider=message_provider,
            ),
            SubmitEditGuessRoute(
                guesses_service=guesses_service,
            ),
            ActionManageGameEditGuessRoute(
                message_provider=message_provider,
                games_repository=games_repository,
            ),
            ActionManageGameDeleteGuessRoute(
                message_provider=message_provider,
                games_repository=games_repository,
            ),
            ListGamesRoute(
                games_service=games_service,
                message_provider=message_provider,
            ),
            CreateRoute(
                games_repository=games_repository,
                discord_messaging=discord_messaging,
                message_provider=message_provider,
            ),
            # GuessRoute(
            #     games_repository=games_repository,
            #     message_provider=message_provider,
            #     game_post_manager=game_post_manager,
            # ),
        ]
    )
