from unittest.mock import patch

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand
from eternal_guesses.routes import create
from eternal_guesses.model.discord_response import ResponseType


@patch.object(create, 'games_repository')
@patch.object(create, 'id_generator')
def test_create_generated_id(mock_id_generator, mock_games_repository):
    # Given
    mock_games_repository.get.return_value = None
    mock_id_generator.game_id.return_value = "potatoific-tomatopuss"

    command = DiscordCommand()
    command.options = {}

    event = DiscordEvent()
    event.command = command

    # When
    create.call(event)

    # Then
    mock_games_repository.insert.assert_called()

    args = mock_games_repository.insert.call_args
    game = args[0][0]
    assert game.game_id == "potatoific-tomatopuss"


@patch.object(create, 'games_repository')
def test_create_given_id(mock_games_repository):
    # Given
    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': 'my-game'
    }

    event = DiscordEvent()
    event.command = command

    # When
    create.call(event)

    # Then
    mock_games_repository.insert.assert_called()

    args = mock_games_repository.insert.call_args
    game = args[0][0]
    assert game.game_id == 'my-game'


@patch.object(create, 'games_repository')
def test_create_duplicate_given_id(mock_games_repository):
    # Given: the games_repository will find a game for the given id
    game_id = 'game-id'

    existing_game = Game()
    existing_game.game_id = game_id
    mock_games_repository.get.return_value = existing_game

    command = DiscordCommand()
    command.options = {
        'game-id': game_id
    }

    event = DiscordEvent()
    event.command = command

    # When
    response = create.call(event)

    # Then
    mock_games_repository.insert.assert_not_called()

    # And we should give a response where we keep the original message
    assert response.type.value == ResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value

