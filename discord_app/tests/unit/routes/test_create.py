from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_event import DiscordEvent, DiscordCommand
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl, GamesRepository
from eternal_guesses.routes import create
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeDiscordMessaging

pytestmark = pytest.mark.asyncio


GAME_CREATED_MESSAGE = "Game created."
DUPLICATE_GAME_ID = "Duplicate game id."


@patch.object(create, 'datetime', autospec=True)
@patch.object(create, 'id_generator', autospec=True)
async def test_create_generated_id(mock_id_generator, mock_datetime):
    # Given
    guild_id = 1001

    create_datetime = datetime.now()
    mock_datetime.now.return_value = create_datetime

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None
    mock_id_generator.game_id.return_value = "potatoific-tomatopuss"

    create_route = _route(games_repository=mock_games_repository)

    # When
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="create",
            options={}
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
    response = await create_route.call(event)

    # Then
    mock_games_repository.save.assert_called()

    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.guild_id == guild_id
    assert game.game_id == "potatoific-tomatopuss"
    assert game.create_datetime == create_datetime
    assert game.close_datetime is None
    assert game.closed is False

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


@patch.object(create, 'datetime', autospec=True)
async def test_create_given_id(mock_datetime):
    # Given
    guild_id = 1002
    game_id = 'prolific-platypus'

    create_datetime = datetime.now()
    mock_datetime.now.return_value = create_datetime

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None

    create_route = _route(games_repository=mock_games_repository)

    # When
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="create",
            options={
                'game-id': game_id
            }
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
    response = await create_route.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)

    mock_games_repository.save.assert_called()
    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.guild_id == guild_id
    assert game.game_id == game_id
    assert game.create_datetime == create_datetime
    assert game.close_datetime is None
    assert game.closed is False

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


async def test_create_duplicate_given_id():
    # Given: the games_repository will find a game for the given id
    guild_id = 1003
    game_id = 'boonful-boonanza'

    existing_game = Game()
    existing_game.game_id = game_id

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = existing_game

    create_route = _route(games_repository=mock_games_repository)

    # When
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="create",
            options={
                'game-id': game_id
            }
        ),
        guild_id=guild_id
    )
    response = await create_route.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.save.assert_not_called()

    assert response.is_ephemeral
    assert response.content == DUPLICATE_GAME_ID


async def test_create_sets_created_by_to_calling_user():
    # Given
    calling_user_id = 500

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None

    event = DiscordEvent(
        command=DiscordCommand(
            command_name="create",
            options={
                'game-id': 'game-id'
            }
        ),
        guild_id=1000,
        member=DiscordMember(
            user_id=calling_user_id
        )
    )

    # When
    create_route = _route(games_repository=mock_games_repository)
    await create_route.call(event)

    # Then
    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.created_by == calling_user_id


async def test_create_sets_title_and_description():
    # Given
    title = "This is the title"
    description = "This is the description"

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None

    event = _make_event(description, title)

    # When
    create_route = _route(games_repository=mock_games_repository)
    response = await create_route.call(event)

    # Then
    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.title == title
    assert game.description == description

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


def _make_event(
        description="",
        title=""):
    return DiscordEvent(
        command=DiscordCommand(
            command_name="create",
            options={
                'game-id': 'game-id',
                'title': title,
                'description': description,
            }
        ),
        guild_id=1000,
        member=DiscordMember(),
    )


def _route(games_repository: GamesRepository = None,
           discord_messaging: DiscordMessaging = None,
           message_provider: MessageProvider = None):
    if games_repository is None:
        games_repository = GamesRepository()

    if discord_messaging is None:
        discord_messaging = FakeDiscordMessaging()

    if message_provider is None:
        message_provider = MagicMock(MessageProvider)
        message_provider.game_created.return_value = GAME_CREATED_MESSAGE
        message_provider.duplicate_game_id.return_value = DUPLICATE_GAME_ID

    return CreateRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )
