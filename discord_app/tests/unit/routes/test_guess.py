from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord_event import DiscordCommand, DiscordEvent, DiscordMember
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes import guess
from eternal_guesses.routes.guess import GuessRoute
from tests.fakes import FakeDiscordMessaging

pytestmark = pytest.mark.asyncio


@patch.object(guess, 'datetime', autospec=True)
async def test_guess_updates_game_guesses(mock_datetime):
    # Given
    game_id = 'game-id'
    guild_id = 'guild-1'
    other_user_id = 5000

    user_id = 100
    user_nickname = 'user-1'
    guess_answer = '42'
    guess_timestamp = datetime.now()

    mock_datetime.now.return_value = guess_timestamp

    existing_game = Game()
    existing_game.guild_id = guild_id
    existing_game.game_id = game_id
    existing_game.guesses = {
        other_user_id: GameGuess(),
    }

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = existing_game

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging)
    event = create_guess_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        user_nickname=user_nickname)
    await guess_route.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)

    mock_games_repository.save.assert_called()
    call_args = mock_games_repository.save.call_args

    saved_game = call_args[0][0]
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
    user_id = 12000
    channel_message_1 = ChannelMessage(1000, 5000)
    channel_message_2 = ChannelMessage(1005, 5005)

    list_guesses_message = "message with new gues"
    mock_message_formatter.channel_list_game_guesses.return_value = list_guesses_message

    game = Game(game_id='game-id', channel_messages=[channel_message_1, channel_message_2])

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = game

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging)
    event = create_guess_event('guild-id', game.game_id, user_id, 'nickname')
    await guess_route.call(event)

    # Then
    update_channel_message_calls = fake_discord_messaging.updated_channel_messages
    assert len(update_channel_message_calls) == 2
    assert {'channel_id': channel_message_1.channel_id, 'message_id': channel_message_1.message_id,
            'text': list_guesses_message} in update_channel_message_calls
    assert {'channel_id': channel_message_1.channel_id, 'message_id': channel_message_1.message_id,
            'text': list_guesses_message} in update_channel_message_calls

    mock_message_formatter.channel_list_game_guesses.assert_called()
    assert user_id in mock_message_formatter.channel_list_game_guesses.call_args.args[0].guesses.keys()


@patch.object(guess, 'message_formatter', autospec=True)
async def test_guess_sends_dm_to_user(mock_message_formatter):
    # Given
    user_id = 13000

    dm_message = "message with new gues"
    mock_message_formatter.dm_guess_added.return_value = dm_message

    game = Game()
    game.game_id = 'game-id'

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = game

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging)
    event = create_guess_event('guild-id', game.game_id, user_id, 'nickname')
    await guess_route.call(event)

    # Then
    assert {'member': event.member, 'text': dm_message} in fake_discord_messaging.sent_dms


@patch.object(guess, 'message_formatter', autospec=True)
async def test_guess_game_does_not_exist(mock_message_formatter: MagicMock):
    # Given
    guild_id = 'guild-3'
    game_id = 'fun-game'
    user_id = 'user-5'

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = None

    event = create_guess_event(guild_id, game_id, user_id, 'nickname')

    dm_error = "error dm"
    mock_message_formatter.dm_error_game_not_found.return_value = dm_error

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging)
    await guess_route.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.save.assert_not_called()

    assert {'member': event.member, 'text': dm_error} in fake_discord_messaging.sent_dms


async def test_guess_duplicate_guess():
    # Given
    game_id = 'game-id'

    existing_game = Game()
    existing_game.game_id = game_id
    existing_game.guesses = {
        'user': '100',
    }

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = existing_game

    # And: we add our guess '42'
    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'guess': '150'
    }

    member = DiscordMember()
    member.user_id = 'user'

    event = DiscordEvent()
    event.command = command
    event.member = member

    fake_discord_messaging = FakeDiscordMessaging()

    # When
    guess_route = GuessRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging)
    await guess_route.call(event)

    # Then
    mock_games_repository.save.assert_not_called()

    assert fake_discord_messaging.sent_dms[0]['member'].user_id == member.user_id


def create_guess_event(guild_id, game_id, user_id, user_nickname):
    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'guess': '42'
    }

    member = DiscordMember()
    member.user_id = user_id
    member.nickname = user_nickname

    event = DiscordEvent()
    event.command = command
    event.member = member
    event.guild_id = guild_id

    return event
