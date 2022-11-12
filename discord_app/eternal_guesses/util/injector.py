import boto3

from eternal_guesses.api.api_authorizer import ApiAuthorizerImpl, \
    ApiAuthorizer
from eternal_guesses.api.discord_event_handler import DiscordEventHandler
from eternal_guesses.api.router import Router, RouterImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from eternal_guesses.routes.actions.action_game_guess import \
    ActionGameGuessRoute
from eternal_guesses.routes.actions.action_manage_game_delete_guess import \
    ActionManageGameDeleteGuessRoute
from eternal_guesses.routes.actions.action_manage_game_edit_guess import \
    ActionManageGameEditGuessRoute
from eternal_guesses.routes.actions.action_manage_game_post import \
    ActionManageGamePostRoute
from eternal_guesses.routes.actions.action_select_delete_guess import \
    ActionSelectDeleteGuessRoute
from eternal_guesses.routes.actions.action_select_edit_guess import \
    ActionSelectEditGuessRoute
from eternal_guesses.routes.actions.action_select_game_to_manage import \
    ActionSelectGameToManageRoute
from eternal_guesses.routes.actions.action_select_post_game import \
    ActionSelectPostGameRoute
from eternal_guesses.routes.commands.create import CreateRoute
from eternal_guesses.routes.commands.guess import GuessRoute
from eternal_guesses.routes.commands.list_games import ListGamesRoute
from eternal_guesses.routes.commands.ping import PingRoute
from eternal_guesses.routes.modal_submits.submit_create import SubmitCreateRoute
from eternal_guesses.routes.modal_submits.submit_edit_guess import \
    SubmitEditGuessRoute
from eternal_guesses.routes.modal_submits.submit_guess import SubmitGuessRoute
from eternal_guesses.services.games_service import GamesService
from eternal_guesses.services.guesses_service import GuessesService
from eternal_guesses.util import app_config
from eternal_guesses.util.discord_messaging import DiscordMessagingImpl
from eternal_guesses.util.game_post_manager import GamePostManagerImpl
from eternal_guesses.util.message_provider import MessageProviderImpl


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
            # ActionManageGameCloseRoute(
            #
            # ),
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
                games_repository=games_repository,
                message_provider=message_provider,
            ),
            CreateRoute(
                games_repository=games_repository,
                discord_messaging=discord_messaging,
                message_provider=message_provider,
            ),
            GuessRoute(
                games_repository=games_repository,
                message_provider=message_provider,
                game_post_manager=game_post_manager,
            ),
        ]
    )
