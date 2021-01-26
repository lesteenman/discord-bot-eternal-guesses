from unittest.mock import patch

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand
from eternal_guesses.model.discord_response import ResponseType
from eternal_guesses.routes import create


@patch.object(create, 'games_repository', autospec=True)
@patch.object(create, 'id_generator', autospec=True)
def test_create_generated_id(mock_id_generator, mock_games_repository):
    # Given
    guild_id = 'guild-1'

    mock_games_repository.get.return_value = None
    mock_id_generator.game_id.return_value = "potatoific-tomatopuss"

    command = DiscordCommand()
    command.options = {}

    event = DiscordEvent()
    event.command = command
    event.guild_id = guild_id

    # When
    create.call(event)

    # Then
    mock_games_repository.put.assert_called()

    args = mock_games_repository.put.call_args

    insert_guild_id = args[0][0]
    assert insert_guild_id == guild_id

    game = args[0][1]
    assert game.guild_id == guild_id
    assert game.game_id == "potatoific-tomatopuss"


@patch.object(create, 'games_repository', autospec=True)
def test_create_given_id(mock_games_repository):
    # Given
    guild_id = 'guild-2'
    game_id = 'prolific-platypus'

    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': game_id
    }

    event = DiscordEvent()
    event.command = command
    event.guild_id = guild_id

    # When
    create.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)

    mock_games_repository.put.assert_called()
    args = mock_games_repository.put.call_args

    insert_guild_id = args[0][0]
    assert insert_guild_id == guild_id

    game = args[0][1]
    assert game.guild_id == guild_id
    assert game.game_id == game_id


@patch.object(create, 'games_repository', autospec=True)
def test_create_duplicate_given_id(mock_games_repository):
    # Given: the games_repository will find a game for the given id
    guild_id = 'guild-3'
    game_id = 'boonful-boonanza'

    existing_game = Game()
    existing_game.game_id = game_id
    mock_games_repository.get.return_value = existing_game

    command = DiscordCommand()
    command.options = {
        'game-id': game_id
    }

    event = DiscordEvent()
    event.command = command
    event.guild_id = guild_id

    # When
    response = create.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.put.assert_not_called()

    # And we should give a response where we keep the original message
    assert response.type.value == ResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value

