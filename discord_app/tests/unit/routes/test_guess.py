from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord.discord_event import DiscordCommand, DiscordEvent, CommandType
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes import guess
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeDiscordMessaging, FakeGamesRepository, FakeMessageProvider

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

    guess_route = GuessRoute(
        games_repository=fake_games_repository,
        discord_messaging=fake_discord_messaging,
        message_provider=FakeMessageProvider()
    )

    # When we make a guess
    event = _create_guess_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        user_nickname=user_nickname,
        guess=guess_answer
    )
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


async def test_guess_updates_channel_messages():
    # Given
    guild_id = 1001
    user_id = 12000
    channel_message_1 = ChannelMessage(channel_id=1000, message_id=5000)
    channel_message_2 = ChannelMessage(channel_id=1005, message_id=5005)

    list_guesses_message = "message with new guess"
    message_provider = MagicMock(MessageProvider)
    message_provider.game_managed_channel_message.return_value = list_guesses_message

    game = Game(
        guild_id=guild_id,
        game_id='game-id',
        channel_messages=[channel_message_1, channel_message_2]
    )

    games_repository = FakeGamesRepository([game])
    discord_messaging = FakeDiscordMessaging()

    guess_route = GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider
    )

    # When
    event = _create_guess_event(guild_id, game.game_id, user_id, 'nickname')
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


async def test_guess_channel_message_gone_silently_fails():
    # Given
    guild_id = 1001
    user_id = 12000
    game_id = 'game-id'
    deleted_channel_message = ChannelMessage(channel_id=1000, message_id=5000)
    other_channel_message = ChannelMessage(channel_id=1000, message_id=5001)

    # We have a game with two channel messages
    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        channel_messages=[deleted_channel_message, other_channel_message]
    )
    games_repository = FakeGamesRepository([game])

    # And we will get a 'not found' error after updating one of those messages
    discord_messaging = FakeDiscordMessaging()
    discord_messaging.raise_404_on_update_of_message(deleted_channel_message.message_id)

    guess_route = GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=FakeMessageProvider(),

    )

    # When we trigger an update
    event = _create_guess_event(guild_id, game.game_id, user_id, 'nickname')
    await guess_route.call(event)

    # Then that channel message is removed from the game
    updated_game = games_repository.get(guild_id=guild_id, game_id=game_id)
    assert len(updated_game.channel_messages) == 1
    assert updated_game.channel_messages[0].message_id == other_channel_message.message_id


async def test_guess_sends_dm_to_user():
    # Given
    guild_id = 1005
    user_id = 13000
    game_id = 'game-id'

    dm_message = "message with new guess"
    message_provider = MagicMock(MessageProvider, autospec=True)
    message_provider.dm_guess_added.return_value = dm_message

    game = Game(guild_id=guild_id, game_id=game_id)
    fake_games_repository = FakeGamesRepository([game])

    fake_discord_messaging = FakeDiscordMessaging()

    guess_route = GuessRoute(
        games_repository=fake_games_repository,
        discord_messaging=fake_discord_messaging,
        message_provider=message_provider
    )

    # When
    event = _create_guess_event(guild_id, game.game_id, user_id, 'nickname')
    await guess_route.call(event)

    # Then
    assert {'member': event.member, 'text': dm_message} in fake_discord_messaging.sent_dms


async def test_guess_game_does_not_exist():
    # Given
    guild_id = 1001
    game_id = 'fun-game'
    user_id = 2001
    event_channel_id = 7002
    member = DiscordMember()

    fake_games_repository = FakeGamesRepository([])

    dm_error = "error dm"
    message_provider = MagicMock(MessageProvider)
    message_provider.manage_error_game_not_found.return_value = dm_error

    fake_discord_messaging = FakeDiscordMessaging()

    guess_route = GuessRoute(
        games_repository=fake_games_repository,
        discord_messaging=fake_discord_messaging,
        message_provider=message_provider
    )

    # When
    event = _create_guess_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        event_channel_id=event_channel_id,
        user_nickname='nickname',
        member=member,
    )
    await guess_route.call(event)

    # Then
    assert len(fake_games_repository.get_all(guild_id=guild_id)) == 0

    assert len(fake_discord_messaging.sent_dms) == 1
    assert fake_discord_messaging.sent_dms[0]['member'] == member
    assert fake_discord_messaging.sent_dms[0]['text'] == dm_error


async def test_guess_duplicate_guess():
    # Given
    guild_id = 1000
    game_id = 'game-id'
    event_channel_id = 7002
    guessing_user_id = 2000
    member = DiscordMember(
        user_id=guessing_user_id,
    )

    old_guess = '100'
    new_guess = '100'
    existing_guesses = {
        guessing_user_id: GameGuess(
            user_id=guessing_user_id,
            guess=old_guess
        ),
    }

    # We have a game
    existing_game = Game(
        guild_id=guild_id,
        game_id=game_id,
        guesses=existing_guesses
    )
    games_repository = FakeGamesRepository(games=[existing_game])

    discord_messaging = FakeDiscordMessaging()
    guess_route = GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=FakeMessageProvider()
    )

    # When we guess '42' as the same user
    event = _create_guess_event(
        guild_id=guild_id,
        user_id=guessing_user_id,
        game_id=game_id,
        guess=new_guess,
        event_channel_id=event_channel_id,
        member=member,
    )
    await guess_route.call(event)

    # Then no new guess is added
    saved_game = games_repository.get(guild_id, existing_game.game_id)
    assert saved_game.guesses[guessing_user_id].guess == old_guess

    # And a DM is sent to the user guessing
    assert discord_messaging.sent_dms[0]['member'] == member


async def test_guess_closed_game():
    # Given
    guild_id = 1515
    game_id = 'closed-game'
    guessing_user_id = 3000
    other_user_id = 3050
    event_channel_id = 7775
    member = DiscordMember()

    # We have a closed game
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=True,
        guesses={
            other_user_id: GameGuess(),
        }
    )
    games_repository = FakeGamesRepository([game])

    discord_messaging = FakeDiscordMessaging()

    route = GuessRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=FakeMessageProvider(),
    )

    # When
    event = _create_guess_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=guessing_user_id,
        event_channel_id=event_channel_id,
        member=member,
    )
    await route.call(event)

    # Then: no guess is added
    saved_game = games_repository.get(guild_id, game_id)
    assert list(saved_game.guesses.keys()) == [other_user_id]

    # And a DM is sent to the user guessing
    assert discord_messaging.sent_dms[0]['member'] == member


def _create_guess_event(guild_id: int, game_id: str, user_id: int = -1, user_nickname: str = 'nickname',
                        guess: str = 'not-relevant', event_channel_id: int = -1, member: DiscordMember = None):
    if member is None:
        member = DiscordMember(
            user_id=user_id,
            nickname=user_nickname
        )

    event = DiscordEvent(
        channel_id=event_channel_id,
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id=-1,
            command_name="guess",
            options={
                'game-id': game_id,
                'guess': guess,
            }
        ),
        member=member,
        guild_id=guild_id,
    )

    return event
