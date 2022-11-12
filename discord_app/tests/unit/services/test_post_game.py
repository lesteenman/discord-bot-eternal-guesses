from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.services.games_service import GamesService
from eternal_guesses.util.game_post_manager import GamePostManager
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_post_creates_channel_message():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    # We have a game
    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    post_message_id = 500
    game_post_manager = MagicMock(GamePostManager)
    game_post_manager.post.return_value = post_message_id

    service = GamesService(
        games_repository=games_repository,
        game_post_manager=game_post_manager,
    )

    # When we post a channel message for our game with an explicit channel
    await service.post(
        guild_id=guild_id,
        game_id=game_id,
        channel_id=channel_id,
    )

    # Then a message about that game is posted in the given channel
    game_post_manager.post.assert_called_with(game, channel_id)

    # And the channel id is saved in the game
    saved_game = games_repository.get(guild_id, game_id)
    assert len(saved_game.channel_messages) == 1
    message = saved_game.channel_messages[0]
    assert message.message_id == post_message_id
