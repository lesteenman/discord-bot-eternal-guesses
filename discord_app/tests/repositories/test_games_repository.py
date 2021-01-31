from datetime import datetime
from unittest.mock import patch

from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.repositories import games_repository
from eternal_guesses.repositories.games_repository import GamesRepository


@patch.object(games_repository, 'boto3', autospec=True)
def test_get_unknown_game_returns_none(mock_boto_3, mocker):
    # Given
    mock_table = mocker.MagicMock()
    mock_table.get_item.return_value = {
        'ResponseMetadata': {}
    }

    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_boto_3.resource.return_value = mock_dynamodb

    # When
    game = GamesRepository.get('guild-id', 'unknown-game-id')

    # Then
    assert game is None


@patch.object(games_repository, 'boto3', autospec=True)
def test_get_game(mock_boto_3, mocker):
    # Given
    guild_id = 50
    game_id = 'game-1'
    user_id = 'user-id'
    guess = 'user-guess'
    message_channel_id = 1000
    message_message_id = 2000
    create_datetime = datetime(2021, 1, 1, 10, 12, 45)
    close_datetime = datetime(2021, 1, 5, 8, 6, 3)

    mock_table = mocker.MagicMock()
    mock_table.get_item.return_value = {
        'ResponseMetadata': {},
        'Item': {
            'pk': f"GUILD#{guild_id}",
            'sk': f"GAME#{game_id}",
            'create_datetime': create_datetime.isoformat(),
            'close_datetime': close_datetime.isoformat(),
            'closed': True,
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
    assert game.create_datetime == create_datetime
    assert game.close_datetime == close_datetime
    assert game.closed is True
    assert user_id in game.guesses
    assert game.guesses[user_id] == guess

    assert len(game.channel_messages) == 1
    assert game.channel_messages[0].channel_id == message_channel_id
    assert game.channel_messages[0].message_id == message_message_id


@patch.object(games_repository, 'boto3', autospec=True)
def test_get_all_games(mock_boto_3, mocker):
    # Given
    guild_id = 50000

    game_1_id = 'game-1'
    game_1_channel_message_channel_id = 1000
    game_1_channel_message_message_id = 2000
    game_1_create_datetime = datetime(2020, 2, 7)

    game_2_id = 'game-2'
    game_2_guess_user_id = 3000
    game_2_guess = 'overninethousand'
    game_2_create_datetime = datetime(2021, 2, 2)

    game_1_item = {
        'pk': f"GUILD#{guild_id}",
        'sk': f"GAME#{game_1_id}",
        'create_datetime': game_1_create_datetime.isoformat(),
        'channel_messages': [
            {'channel_id': game_1_channel_message_channel_id,
                'message_id': game_1_channel_message_message_id}
        ],
    }

    game_2_item = {
        'pk': f"GUILD#{guild_id}",
        'sk': f"GAME#{game_2_id}",
        'create_datetime': game_2_create_datetime.isoformat(),
        'guesses': {
            game_2_guess_user_id: game_2_guess
        },
    }

    mock_table = mocker.MagicMock()
    mock_table.query.return_value = {
        'ResponseMetadata': {},
        'Items': [game_1_item, game_2_item],
    }

    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_boto_3.resource.return_value = mock_dynamodb

    # When
    games = GamesRepository.get_all(guild_id)

    # Then
    assert len(games) == 2

    game_1 = None
    game_2 = None

    for game in games:
        if game.game_id == game_1_id:
            game_1 = game
        elif game.game_id == game_2_id:
            game_2 = game

    assert game_1 is not None
    assert game_1.guild_id == guild_id
    assert game_1.game_id == game_1_id
    assert game_1.create_datetime == game_1_create_datetime
    assert game_1.close_datetime is None
    assert game_1.closed is False
    assert game_1.guesses == {}

    assert len(game_1.channel_messages) == 1
    assert game_1.channel_messages[0].channel_id == game_1_channel_message_channel_id
    assert game_1.channel_messages[0].message_id == game_1_channel_message_message_id

    assert game_2 is not None
    assert game_2.guild_id == guild_id
    assert game_2.game_id == game_2_id
    assert game_2.create_datetime == game_2_create_datetime
    assert game_2.close_datetime is None
    assert game_2.closed is False
    assert game_2.channel_messages == []

    assert game_2_guess_user_id in game_2.guesses
    assert game_2.guesses[game_2_guess_user_id] == game_2_guess


@patch.object(games_repository, 'boto3', autospec=True)
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
    game.closed = True
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
        'closed': True,
        'guesses': {
            user_id: guess,
        },
        'channel_messages': [
            {'channel_id': message_channel_id, 'message_id': message_message_id},
        ]
    })
