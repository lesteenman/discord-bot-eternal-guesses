from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.services.games_service import GamesService
from eternal_guesses.util.game_post_manager import GamePostManager
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_close():
    # Given
    guild_id = 1007
    game_id = 'game-id-1'

    # We have an open game
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=False
    )
    games_repository = FakeGamesRepository([game])

    game_closed_message = "Game closed."
    message_provider = MagicMock(MessageProvider)
    message_provider.game_closed.return_value = game_closed_message

    game_post_manager = MagicMock(GamePostManager)

    service = GamesService(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    # When we close it
    await service.close(
        guild_id=guild_id,
        game_id=game_id,
    )

    # Then it should be closed
    saved_game = games_repository.get(guild_id, game.game_id)
    assert saved_game.closed

    game_post_manager.update.assert_called_with(game)
