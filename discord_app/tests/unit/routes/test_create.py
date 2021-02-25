from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, CommandType
from eternal_guesses.model.discord_member import DiscordMember
from eternal_guesses.model.discord_response import ResponseType
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from eternal_guesses.routes import create
from eternal_guesses.routes.create import CreateRoute

pytestmark = pytest.mark.asyncio


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

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="create",
            options={}
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )

    # When
    create_route = CreateRoute(games_repository=mock_games_repository)
    await create_route.call(event)

    # Then
    mock_games_repository.save.assert_called()

    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.guild_id == guild_id
    assert game.game_id == "potatoific-tomatopuss"
    assert game.create_datetime == create_datetime
    assert game.close_datetime is None
    assert game.closed is False


@patch.object(create, 'datetime', autospec=True)
async def test_create_given_id(mock_datetime):
    # Given
    guild_id = 1002
    game_id = 'prolific-platypus'

    create_datetime = datetime.now()
    mock_datetime.now.return_value = create_datetime

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="create",
            options={
                'game-id': game_id
            }
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )

    # When
    create_route = CreateRoute(games_repository=mock_games_repository)
    await create_route.call(event)

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


async def test_create_duplicate_given_id():
    # Given: the games_repository will find a game for the given id
    guild_id = 1003
    game_id = 'boonful-boonanza'

    existing_game = Game()
    existing_game.game_id = game_id

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = existing_game

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="create",
            options={
                'game-id': game_id
            }
        ),
        guild_id=guild_id
    )

    # When
    create_route = CreateRoute(games_repository=mock_games_repository)
    response = await create_route.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.save.assert_not_called()

    # And we should give a response where we keep the original message
    assert response.response_type.value == ResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value


async def test_create_sets_created_by_to_calling_user():
    # Given
    calling_user_id = 500

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
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
    create_route = CreateRoute(games_repository=mock_games_repository)
    await create_route.call(event)

    # Then
    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.created_by == calling_user_id
