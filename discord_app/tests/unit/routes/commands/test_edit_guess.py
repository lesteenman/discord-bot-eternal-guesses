import typing
from unittest.mock import MagicMock, AsyncMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.edit_guess import EditGuessRoute
from eternal_guesses.util.game_post_manager import GamePostManager
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_edit_guess():
    # Given
    guild_id = 10
    game_id = "game-1"
    guessing_player_id = 100
    old_guess = "<My Guess>"

    guess_edited_message = "Guess has been edited."
    message_provider = MagicMock(MessageProvider)
    message_provider.guess_edited.return_value = guess_edited_message

    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        guesses={
            guessing_player_id: GameGuess(
                user_id=guessing_player_id,
                guess=old_guess,
            )
        }
    )
    games_repository = FakeGamesRepository(games=[game])

    game_post_manager = AsyncMock(GamePostManager)

    route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )

    # When
    new_guess = "500"
    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game_id,
            'member': str(guessing_player_id),
            'guess': new_guess,
        }
    )
    response = await route.call(event)

    # Then
    updated_game = games_repository.get(guild_id, game_id)
    assert updated_game.guesses[guessing_player_id].guess == new_guess

    game_post_manager.update.assert_called_with(game)

    assert response.is_ephemeral
    assert response.content == guess_edited_message


async def test_edit_guess_does_not_exist():
    # Given
    guild_id = 10
    game_id = "game-1"
    delete_member_id = 200

    guess_not_found_message = "No guess found."
    message_provider = MagicMock(MessageProvider)
    message_provider.error_guess_not_found.return_value = guess_not_found_message

    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        guesses={
            -1: GameGuess(
                user_id=-1,
                guess="<your guess>",
            )
        }
    )
    games_repository = FakeGamesRepository(games=[game])

    game_post_manager = AsyncMock(GamePostManager)

    route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )

    # When
    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game_id,
            'member': str(delete_member_id),
            'guess': "some new guess",
        }
    )
    response = await route.call(event)

    # Then
    game_post_manager.update.assert_not_called()

    assert response.is_ephemeral
    assert response.content == guess_not_found_message


async def test_edit_guess_game_does_not_exist():
    # Given
    guild_id = 10
    game_id = "game-1"
    guessing_player_id = 100

    game_not_found_message = "No game found."
    message_provider = MagicMock(MessageProvider)
    message_provider.error_game_not_found.return_value = game_not_found_message

    games_repository = FakeGamesRepository(games=[])

    route = _route(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When
    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game_id,
            'member': str(guessing_player_id),
            'guess': "some new guess",
        }
    )
    response = await route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == game_not_found_message


def _make_event(guild_id: int = -1, options: typing.Dict = None, discord_member: DiscordMember = None,
                channel_id: int = -1):
    if options is None:
        options = {}

    if discord_member is None:
        discord_member = DiscordMember()

    return DiscordEvent(
        guild_id=guild_id,
        channel_id=channel_id,
        command=DiscordCommand(
            command_name="manage",
            subcommand_name="edit-guess",
            options=options,
        ),
        member=discord_member
    )


def _route(games_repository=None, message_provider=None, game_post_manager=None):
    if games_repository is None:
        games_repository = FakeGamesRepository()

    if message_provider is None:
        message_provider = MagicMock(MessageProvider)

    if game_post_manager is None:
        game_post_manager = AsyncMock(GamePostManager)

    return EditGuessRoute(
        games_repository=games_repository,
        message_provider=message_provider,
        game_post_manager=game_post_manager,
    )
