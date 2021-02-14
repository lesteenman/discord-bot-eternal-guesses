from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, DiscordMember
from eternal_guesses.model.discord_response import ResponseType
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes import create
from eternal_guesses.routes.create import CreateRoute

pytestmark = pytest.mark.asyncio


@patch.object(create, 'datetime', autospec=True)
@patch.object(create, 'id_generator', autospec=True)
async def test_create_generated_id(mock_id_generator, mock_datetime):
    # Given
    guild_id = 'guild-1'

    create_datetime = datetime.now()
    mock_datetime.now.return_value = create_datetime

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = None
    mock_id_generator.game_id.return_value = "potatoific-tomatopuss"

    command = DiscordCommand()
    command.options = {}

    event = DiscordEvent()
    event.command = command
    event.guild_id = guild_id
    event.member = DiscordMember()

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
    guild_id = 'guild-2'
    game_id = 'prolific-platypus'

    create_datetime = datetime.now()
    mock_datetime.now.return_value = create_datetime

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': game_id
    }

    event = DiscordEvent()
    event.command = command
    event.guild_id = guild_id
    event.member = DiscordMember()

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
    guild_id = 'guild-3'
    game_id = 'boonful-boonanza'

    existing_game = Game()
    existing_game.game_id = game_id

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = existing_game

    command = DiscordCommand()
    command.options = {
        'game-id': game_id
    }

    event = DiscordEvent()
    event.command = command
    event.guild_id = guild_id

    # When
    create_route = CreateRoute(games_repository=mock_games_repository)
    response = await create_route.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.save.assert_not_called()

    # And we should give a response where we keep the original message
    assert response.type.value == ResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value


async def test_create_sets_created_by_to_calling_user():
    # Given
    calling_user_id = 500

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': 'game-id'
    }

    calling_member = DiscordMember()
    calling_member.user_id = calling_user_id

    event = DiscordEvent()
    event.command = command
    event.guild_id = 'guild-id'
    event.member = calling_member

    # When
    create_route = CreateRoute(games_repository=mock_games_repository)
    await create_route.call(event)

    # Then
    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.created_by == calling_user_id
