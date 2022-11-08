from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

import discord
import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.discord.discord_modal_submit import \
    DiscordModalSubmit
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes import submit_guess
from eternal_guesses.routes.submit_guess import SubmitGuessRoute
from eternal_guesses.util.game_post_manager import GamePostManager
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository, FakeMessageProvider

pytestmark = pytest.mark.asyncio


@patch.object(submit_guess, 'datetime', autospec=True)
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

    submit_guess_route = _route(
        games_repository=fake_games_repository,
    )

    # When we make a guess
    event = _create_submit_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        user_nickname=user_nickname,
        guess=guess_answer
    )
    await submit_guess_route.call(event)

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

    post_embed = discord.Embed()
    message_provider = MagicMock(MessageProvider)
    message_provider.game_post_embed.return_value = post_embed

    game = Game(
        guild_id=guild_id,
        game_id="game-1",
    )

    games_repository = FakeGamesRepository([game])
    game_post_manager = MagicMock(GamePostManager)

    submit_guess_route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )

    # When
    event = _create_submit_event(guild_id, game.game_id, user_id, 'nickname')
    await submit_guess_route.call(event)

    # Then
    game_post_manager.update.assert_called_with(game)


async def test_guess_replies_with_ephemeral_message():
    # Given
    guild_id = 1005
    user_id = 13000
    game_id = 'game-id'

    response_message = "message with new guess"
    message_provider = MagicMock(MessageProvider, autospec=True)
    message_provider.guess_added.return_value = response_message

    game = Game(guild_id=guild_id, game_id=game_id)
    fake_games_repository = FakeGamesRepository([game])

    submit_guess_route = _route(
        games_repository=fake_games_repository,
        message_provider=message_provider,
    )

    # When
    event = _create_submit_event(guild_id, game.game_id, user_id, 'nickname')
    response = await submit_guess_route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == response_message


async def test_guess_game_does_not_exist():
    # Given
    guild_id = 1001
    game_id = 'fun-game'
    user_id = 2001
    event_channel_id = 7002
    member = DiscordMember()

    fake_games_repository = FakeGamesRepository([])

    error_message = "error dm"
    message_provider = MagicMock(MessageProvider)
    message_provider.error_game_not_found.return_value = error_message

    submit_guess_route = _route(
        games_repository=fake_games_repository,
        message_provider=message_provider,
    )

    # When
    event = _create_submit_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        event_channel_id=event_channel_id,
        user_nickname='nickname',
        member=member,
    )
    response = await submit_guess_route.call(event)

    # Then
    assert len(fake_games_repository.get_all(guild_id=guild_id)) == 0

    assert response.is_ephemeral
    assert response.content == error_message


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

    duplicate_guess_message = "You already placed a guess for this game."
    message_provider = MagicMock(MessageProvider)
    message_provider.error_duplicate_guess.return_value = duplicate_guess_message

    submit_guess_route = _route(
        games_repository=games_repository,
        message_provider=message_provider
    )

    # When we guess '42' as the same user
    event = _create_submit_event(
        guild_id=guild_id,
        user_id=guessing_user_id,
        game_id=game_id,
        guess=new_guess,
        event_channel_id=event_channel_id,
        member=member,
    )
    response = await submit_guess_route.call(event)

    # Then no new guess is added
    saved_game = games_repository.get(guild_id, existing_game.game_id)
    assert saved_game.guesses[guessing_user_id].guess == old_guess

    # And an ephemeral error is the response
    assert response.is_ephemeral
    assert response.content == duplicate_guess_message


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

    duplicate_guess_message = "This game has been closed for new guesses."
    message_provider = MagicMock(MessageProvider)
    message_provider.error_guess_on_closed_game.return_value = duplicate_guess_message

    route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When
    event = _create_submit_event(
        guild_id=guild_id,
        game_id=game_id,
        user_id=guessing_user_id,
        event_channel_id=event_channel_id,
        member=member,
    )
    response = await route.call(event)

    # Then: no guess is added
    saved_game = games_repository.get(guild_id, game_id)
    assert list(saved_game.guesses.keys()) == [other_user_id]

    # And an ephemeral error is the response
    assert response.is_ephemeral
    assert response.content == duplicate_guess_message


async def test_guess_non_numerical_on_numeric_game():
    # Given
    guild_id = 1005
    user_id = 13000
    game_id = 'game-id'

    response_message = "Guess must be a number"
    message_provider = MagicMock(MessageProvider, autospec=True)
    message_provider.invalid_guess.return_value = response_message

    # And we have a game with a min and a max
    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        min_guess=1,
        max_guess=100
    )

    games_repository = FakeGamesRepository([game])
    submit_guess_route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When
    event = _create_submit_event(guild_id, game.game_id, user_id, 'nickname')
    response = await submit_guess_route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == response_message

    # And the guess was not added
    updated_game = games_repository.get(guild_id=guild_id, game_id=game_id)
    assert len(updated_game.guesses) == 0


async def test_guess_higher_than_max():
    # Given
    guild_id = 1005
    user_id = 13000
    game_id = 'game-id'

    max_guess = 100

    response_message = "Guess must be a number below 100"
    message_provider = MagicMock(MessageProvider, autospec=True)
    message_provider.invalid_guess.return_value = response_message

    # And we have a game with a max
    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        max_guess=max_guess,
    )

    games_repository = FakeGamesRepository([game])
    submit_guess_route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When we guess higher than that
    guess = "101"
    event = _create_submit_event(
        guild_id=guild_id,
        game_id=game.game_id,
        user_id=user_id,
        user_nickname='nickname',
        guess=guess,
    )
    response = await submit_guess_route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == response_message

    # And the guess was not added
    updated_game = games_repository.get(guild_id=guild_id, game_id=game_id)
    assert len(updated_game.guesses) == 0


async def test_lower_than_min():
    # Given
    guild_id = 1005
    user_id = 13000
    game_id = 'game-id'

    min_guess = -5

    response_message = "Guess must be a number higher than -5"
    message_provider = MagicMock(MessageProvider, autospec=True)
    message_provider.invalid_guess.return_value = response_message

    # And we have a game with a max
    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        min_guess=min_guess,
    )

    games_repository = FakeGamesRepository([game])
    submit_guess_route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When we guess lower than that
    guess = "-6"
    event = _create_submit_event(
        guild_id=guild_id,
        game_id=game.game_id,
        user_id=user_id,
        user_nickname='nickname',
        guess=guess,
    )
    response = await submit_guess_route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == response_message

    # And the guess was not added
    updated_game = games_repository.get(guild_id=guild_id, game_id=game_id)
    assert len(updated_game.guesses) == 0


def _create_submit_event(
    guild_id: int, game_id: str, user_id: int = -1,
    user_nickname: str = 'nickname',
    guess: str = 'not-relevant', event_channel_id: int = -1,
    member: DiscordMember = None
):
    if member is None:
        member = DiscordMember(
            user_id=user_id,
            nickname=user_nickname
        )

    event = DiscordEvent(
        channel_id=event_channel_id,
        modal_submit=DiscordModalSubmit(
            modal_custom_id=f"modal_submit_guess_{game_id}",
            input_custom_id=f"modal_input_guess_value_{game_id}",
            input_value=guess,
        ),
        member=member,
        guild_id=guild_id,
    )

    return event


def _route(
    games_repository: GamesRepository = None,
    message_provider: MessageProvider = None,
    game_post_manager: GamePostManager = None
):
    if games_repository is None:
        games_repository = FakeGamesRepository([])

    if message_provider is None:
        message_provider = FakeMessageProvider()

    if game_post_manager is None:
        game_post_manager = AsyncMock(GamePostManager, autospec=True)

    submit_guess_route = SubmitGuessRoute(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )
    return submit_guess_route
