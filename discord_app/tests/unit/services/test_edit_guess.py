from unittest.mock import AsyncMock, MagicMock

import pytest

from eternal_guesses.exceptions import GuessNotFoundError, GameNotFoundError
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.services.guesses_service import GuessesService
from eternal_guesses.app.game_post_manager import GamePostManager
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_edit_guess():
    # Given
    guild_id = 10
    game_id = "game-1"
    guessing_player_id = 100
    old_guess = "<My Guess>"

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

    service = _service(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    # When
    new_guess = "500"
    await service.edit(
        guild_id=guild_id,
        game_id=game_id,
        member=guessing_player_id,
        guess=new_guess,
    )

    # Then
    updated_game = games_repository.get(guild_id, game_id)
    assert updated_game.guesses[guessing_player_id].guess == new_guess

    game_post_manager.update.assert_called_with(game)


async def test_edit_guess_does_not_exist():
    # Given
    guild_id = 10
    game_id = "game-1"
    delete_member_id = 200

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
        await service.edit(
            guild_id=guild_id,
            game_id=game_id,
            member=delete_member_id,
            guess='some new guess',
        )

    # Then
    game_post_manager.update.assert_not_called()


async def test_edit_guess_game_does_not_exist():
    # Given
    guild_id = 10
    game_id = "game-1"
    guessing_player_id = 100

    games_repository = FakeGamesRepository(games=[])
    game_post_manager = MagicMock(GamePostManager)

    service = _service(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    # When
    with pytest.raises(GameNotFoundError):
        await service.edit(
            guild_id=guild_id,
            game_id=game_id,
            member=guessing_player_id,
            guess="some new guess",
        )

    # Then
    game_post_manager.update.assert_not_called()


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
