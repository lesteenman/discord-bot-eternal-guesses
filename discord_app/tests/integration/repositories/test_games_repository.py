from datetime import datetime

from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from tests.integration.conftest import TABLE_NAME, HOST


def test_get_unknown_game_returns_none():
    # Given: an empty database
    games_repository = GamesRepositoryImpl(table_name=TABLE_NAME, host=HOST)
    other_game = Game(guild_id=1, game_id='game-id-1', created_by=10)

    # When
    games_repository.save(other_game)
    game = games_repository.get(1, 'game-id-2')

    # Then
    assert game is None


def test_get_minimal_game():
    # Given
    games_repository = GamesRepositoryImpl(table_name=TABLE_NAME, host=HOST)

    game = Game(
        guild_id=1,
        game_id="game-1",
        created_by=10
    )

    # When
    games_repository.save(game)
    retrieved_game = games_repository.get(game.guild_id, game.game_id)

    # Then
    assert game.guild_id == retrieved_game.guild_id
    assert game.game_id == retrieved_game.game_id


def test_get_game():
    # Given
    games_repository = GamesRepositoryImpl(table_name=TABLE_NAME, host=HOST)

    guild_id = 50
    created_by = 120
    game_id = 'game-1'
    user_id = 12123
    user_nickname = 'nickname'
    guess_answer = 'user-guess'
    guess_timestamp = datetime.now()
    message_channel_id = 1000
    message_message_id = 2000
    create_datetime = datetime(2021, 1, 1, 10, 12, 45)
    close_datetime = datetime(2021, 1, 5, 8, 6, 3)
    closed = True

    game = Game(
        guild_id=guild_id,
        created_by=created_by,
        create_datetime=create_datetime,
        close_datetime=close_datetime,
        closed=closed,
        game_id=game_id,
        guesses={
            user_id: GameGuess(
                user_id=user_id,
                nickname=user_nickname,
                guess=guess_answer,
                timestamp=guess_timestamp
            )
        },
        channel_messages=[
            ChannelMessage(channel_id=message_channel_id, message_id=message_message_id)
        ]
    )

    # When
    games_repository.save(game)
    retrieved_game = games_repository.get(guild_id, game_id)

    # Then
    assert retrieved_game.guild_id == guild_id
    assert retrieved_game.game_id == game_id
    assert retrieved_game.created_by == created_by
    assert retrieved_game.create_datetime == create_datetime
    assert retrieved_game.close_datetime == close_datetime
    assert retrieved_game.closed is closed

    assert user_id in retrieved_game.guesses

    game_guess = retrieved_game.guesses[user_id]
    assert game_guess.user_id == user_id
    assert game_guess.nickname == user_nickname
    assert game_guess.guess == guess_answer
    assert game_guess.timestamp == guess_timestamp

    assert len(retrieved_game.channel_messages) == 1
    assert retrieved_game.channel_messages[0].channel_id == message_channel_id
    assert retrieved_game.channel_messages[0].message_id == message_message_id


def test_get_all_games_without_games():
    # Given
    games_repository = GamesRepositoryImpl(table_name=TABLE_NAME, host=HOST)

    # When
    games = games_repository.get_all(1)

    # Then
    assert len(games) == 0


def test_get_all_games():
    # Given
    games_repository = GamesRepositoryImpl(table_name=TABLE_NAME, host=HOST)

    guild_id = 50000

    game_1_id = 'game-1'
    game_1_created_by = 10
    game_1_channel_message_channel_id = 1000
    game_1_channel_message_message_id = 2000
    game_1_create_datetime = datetime(2020, 2, 7)

    game_2_id = 'game-2'
    game_2_created_by = 20
    game_2_guess_user_id = 3000
    game_2_guess_user_nick = 'user-nick'
    game_2_guess_answer = 'guess-answer'
    game_2_guess_timestamp = datetime(2021, 2, 3, 10, 10, 10)
    game_2_create_datetime = datetime(2021, 2, 2)

    game_1 = Game(
        guild_id=guild_id,
        game_id=game_1_id,
        created_by=game_1_created_by,
        create_datetime=game_1_create_datetime,
        channel_messages=[
            ChannelMessage(channel_id=game_1_channel_message_channel_id, message_id=game_1_channel_message_message_id),
        ]
    )

    game_2 = Game(
        guild_id=guild_id,
        game_id=game_2_id,
        created_by=game_2_created_by,
        create_datetime=game_2_create_datetime,
        guesses={
            game_2_guess_user_id: GameGuess(
                user_id=game_2_guess_user_id,
                nickname=game_2_guess_user_nick,
                guess=game_2_guess_answer,
                timestamp=game_2_guess_timestamp
            )
        }
    )

    # When
    games_repository.save(game_1)
    games_repository.save(game_2)
    games = games_repository.get_all(guild_id)

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
    assert game_1.created_by == game_1_created_by
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
    assert game_2.created_by == game_2_created_by
    assert game_2.create_datetime == game_2_create_datetime
    assert game_2.close_datetime is None
    assert game_2.closed is False
    assert game_2.channel_messages == []

    assert game_2_guess_user_id in game_2.guesses
    game_guess = game_2.guesses[game_2_guess_user_id]
    assert game_guess.user_id == game_2_guess_user_id
    assert game_guess.nickname == game_2_guess_user_nick
    assert game_guess.guess == game_2_guess_answer
    assert game_guess.timestamp == game_2_guess_timestamp
