from datetime import datetime
from unittest.mock import patch

import pytest

from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord_event import DiscordCommand, DiscordEvent, DiscordMember, CommandType
from eternal_guesses.routes import guess
from eternal_guesses.routes.guess import GuessRoute
from tests.fakes import FakeDiscordMessaging, FakeGamesRepository

pytestmark = pytest.mark.asyncio


@patch.object(guess, 'datetime', autospec=True)
async def test_guess_updates_game_guesses(mock_datetime):
    # Given
    game_id = 'game-id'
    guild_id = 1000
    other_user_id = 5000

    user_id = 100
    user_nickname = 'user-1'
    guess_answer = '42'
    guess_timestamp = datetime.now()

    mock_datetime.now.return_value = guess_timestamp

    existing_game = Game(
        guild_id=guild_id,
        game_id=game_id,
        guesses={
            other_user_id: GameGuess(),
        }
    )

    fake_games_repository = FakeGamesRepository([existing_game])
    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(
        games_repository=fake_games_repository,
        discord_messaging=fake_discord_messaging)

    event = create_guess_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        user_nickname=user_nickname)
    await guess_route.call(event)

    # Then
    saved_game = fake_games_repository.get(guild_id, game_id)
    assert saved_game.guild_id == guild_id
    assert saved_game.game_id == game_id
    assert other_user_id in saved_game.guesses.keys()

    saved_guess = saved_game.guesses[user_id]
    assert saved_guess.user_id == user_id
    assert saved_guess.user_nickname == user_nickname
    assert saved_guess.timestamp == guess_timestamp
    assert saved_guess.guess == guess_answer


@patch.object(guess, 'message_formatter', autospec=True)
async def test_guess_updates_channel_messages(mock_message_formatter):
    # Given
    guild_id = 1001
    user_id = 12000
    channel_message_1 = ChannelMessage(channel_id=1000, message_id=5000)
    channel_message_2 = ChannelMessage(channel_id=1005, message_id=5005)

    list_guesses_message = "message with new gues"
    mock_message_formatter.channel_list_game_guesses.return_value = list_guesses_message

    game = Game(
        guild_id=guild_id,
        game_id='game-id',
        channel_messages=[channel_message_1, channel_message_2]
    )

    games_repository = FakeGamesRepository([game])
    discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging
    )
    event = create_guess_event(guild_id, game.game_id, user_id, 'nickname')
    await guess_route.call(event)

    # Then
    update_channel_message_calls = discord_messaging.updated_channel_messages
    assert len(update_channel_message_calls) == 2
    assert {
               'channel_id': channel_message_1.channel_id,
               'message_id': channel_message_1.message_id,
               'text': list_guesses_message
           } in update_channel_message_calls
    assert {
               'channel_id': channel_message_1.channel_id,
               'message_id': channel_message_1.message_id,
               'text': list_guesses_message
           } in update_channel_message_calls

    mock_message_formatter.channel_list_game_guesses.assert_called()
    assert user_id in mock_message_formatter.channel_list_game_guesses.call_args.args[0].guesses.keys()


@patch.object(guess, 'message_formatter', autospec=True)
async def test_guess_sends_dm_to_user(mock_message_formatter):
    # Given
    guild_id = 1005
    user_id = 13000
    game_id = 'game-id'

    dm_message = "message with new gues"
    mock_message_formatter.dm_guess_added.return_value = dm_message

    game = Game(guild_id=guild_id, game_id=game_id)

    fake_games_repository = FakeGamesRepository([game])
    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(
        games_repository=fake_games_repository,
        discord_messaging=fake_discord_messaging)
    event = create_guess_event(guild_id, game.game_id, user_id, 'nickname')
    await guess_route.call(event)

    # Then
    assert {'member': event.member, 'text': dm_message} in fake_discord_messaging.sent_dms


@patch.object(guess, 'message_formatter', autospec=True)
async def test_guess_game_does_not_exist(mock_message_formatter):
    # Given
    guild_id = 1001
    game_id = 'fun-game'
    user_id = 2001

    fake_games_repository = FakeGamesRepository([])
    event = create_guess_event(guild_id, game_id, user_id, 'nickname')

    dm_error = "error dm"
    mock_message_formatter.dm_error_game_not_found.return_value = dm_error

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(
        games_repository=fake_games_repository,
        discord_messaging=fake_discord_messaging)
    await guess_route.call(event)

    # Then
    assert len(fake_games_repository.get_all(guild_id=guild_id)) == 0

    assert {'member': event.member, 'text': dm_error} in fake_discord_messaging.sent_dms


async def test_guess_duplicate_guess():
    # Given
    guild_id = 1000
    game_id = 'game-id'

    existing_game = Game(
        guild_id=guild_id,
        game_id=game_id,
        guesses={
            1000: GameGuess(),
        }
    )

    fake_games_repository = FakeGamesRepository(games=[existing_game])

    # And: we add our guess '42'
    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="guess",
            options={
                'game-id': game_id,
                'guess': '150'
            }
        ),
        member=DiscordMember(
            user_id=2000
        )
    )

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(games_repository=fake_games_repository, discord_messaging=fake_discord_messaging)
    await guess_route.call(event)

    # Then
    assert fake_games_repository.get_all(guild_id) == [existing_game]

    assert fake_discord_messaging.sent_dms[0]['member'].user_id == DiscordMember(
        user_id=2000
    ).user_id


def create_guess_event(guild_id: int, game_id: str, user_id: int, user_nickname: str):
    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="guess",
            options={
                'game-id': game_id,
                'guess': '42'
            }
        ),
        member=DiscordMember(
            user_id=user_id,
            nickname=user_nickname
        ),
        guild_id=guild_id
    )

    return event
