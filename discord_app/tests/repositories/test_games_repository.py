from unittest.mock import patch

from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.repositories import games_repository
from eternal_guesses.repositories.games_repository import GamesRepository


@patch.object(games_repository, 'boto3')
def test_get_unknown_game_returns_none(mock_boto_3, mocker):
    # Given
    mock_table = mocker.MagicMock()
    mock_table.get_item.return_value = {
        'TableInfo': {}
    }

    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_boto_3.resource.return_value = mock_dynamodb

    # When
    game = GamesRepository.get('guild-id', 'unknown-game-id')

    # Then
    assert game is None


@patch.object(games_repository, 'boto3')
def test_get_game(mock_boto_3, mocker):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    user_id = 'user-id'
    guess = 'user-guess'
    message_channel_id = 1000
    message_message_id = 2000

    mock_table = mocker.MagicMock()
    mock_table.get_item.return_value = {
        'TableInfo': {},
        'Item': {
            'pk': f"GUILD#{guild_id}",
            'sk': f"GAME#{game_id}",
            'guesses': {
                user_id: guess
            },
            'channel_messages': [
                {'channel_id': message_channel_id,
                    'message_id': message_message_id}
            ],
        }
    }

    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_boto_3.resource.return_value = mock_dynamodb

    # When
    game = GamesRepository.get(guild_id, game_id)

    # Then
    assert game.guild_id == guild_id
    assert game.game_id == game_id
    assert user_id in game.guesses
    assert game.guesses[user_id] == guess

    assert len(game.channel_messages) == 1
    assert game.channel_messages[0].channel_id == message_channel_id
    assert game.channel_messages[0].message_id == message_message_id


@patch.object(games_repository, 'boto3')
def test_save_game(mock_boto_3, mocker):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    user_id = 'user-id'
    guess = 'user-guess'
    message_channel_id = 1000
    message_message_id = 2000

    mock_table = mocker.MagicMock()

    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_boto_3.resource.return_value = mock_dynamodb

    game = Game()
    game.guild_id = guild_id
    game.game_id = game_id
    game.guesses = {
        user_id: guess,
    }
    game.channel_messages = [
        ChannelMessage(
            channel_id=message_channel_id,
            message_id=message_message_id),
    ]

    # When
    GamesRepository.save(guild_id, game)

    # Then
    mock_table.put_item.assert_called_with(Item={
        'pk': f"GUILD#{guild_id}",
        'sk': f"GAME#{game_id}",
        'guesses': {
            user_id: guess,
        },
        'channel_messages': [
            {'channel_id': message_channel_id, 'message_id': message_message_id},
        ]
    })
