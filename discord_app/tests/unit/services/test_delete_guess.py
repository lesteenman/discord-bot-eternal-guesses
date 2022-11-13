from unittest.mock import MagicMock, AsyncMock

import pytest

from eternal_guesses.exceptions import GuessNotFoundError, GameNotFoundError
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.services.guesses_service import GuessesService
from eternal_guesses.app.game_post_manager import GamePostManager
from eternal_guesses.app.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_delete_guess():
    # Given
    guild_id = 10
    game_id = "game-1"
    guessing_player_id = 100

    game = Game(
        guild_id=guild_id,
        game_id=game_id,
        guesses={
            guessing_player_id: GameGuess(
                user_id=guessing_player_id,
                guess="<your guess>",
            )
        }
    )
    games_repository = FakeGamesRepository(games=[game])

    game_post_manager = AsyncMock(GamePostManager)

    service = _service(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    # When
    await service.delete(
        guild_id=guild_id,
        game_id=game_id,
        member=guessing_player_id,
    )

    # Then
    updated_game = games_repository.get(guild_id, game_id)
    assert guessing_player_id not in updated_game.guesses

    # ToDo: check with fake
    game_post_manager.update.assert_called_with(game)


async def test_delete_guess_does_not_exist():
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

    service = _service(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    # When
    with pytest.raises(GuessNotFoundError):
        await service.delete(
            guild_id=guild_id,
            game_id=game_id,
            member=delete_member_id,
        )

    # Then
    game_post_manager.update.assert_not_called()


async def test_delete_guess_game_does_not_exist():
    # Given
    guild_id = 10
    game_id = "game-1"
    guessing_player_id = 100

    game_not_found_message = "No game found."
    message_provider = MagicMock(MessageProvider)
    message_provider.error_game_not_found.return_value = game_not_found_message

    games_repository = FakeGamesRepository(games=[])

    service = _service(
        games_repository=games_repository,
    )

    # When
    with pytest.raises(GameNotFoundError):
        await service.delete(
            guild_id=guild_id,
            game_id=game_id,
            member=guessing_player_id,
        )


def _service(
    games_repository=None,
    game_post_manager=None
):
    if games_repository is None:
        games_repository = FakeGamesRepository()

    if game_post_manager is None:
        game_post_manager = AsyncMock(GamePostManager)

    return GuessesService(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )
