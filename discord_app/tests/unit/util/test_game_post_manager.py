from unittest.mock import MagicMock

import discord
import pytest

from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.data.game import Game
from eternal_guesses.util.game_post_manager import GamePostManagerImpl
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository, FakeDiscordMessaging

pytestmark = pytest.mark.asyncio


async def test_update_post():
    # Given
    game_post_1 = ChannelMessage(channel_id=1000, message_id=5000)
    game_post_2 = ChannelMessage(channel_id=1005, message_id=5005)

    post_embed = discord.Embed()
    message_provider = MagicMock(MessageProvider)
    message_provider.game_post_embed.return_value = post_embed

    game = Game(
        game_id='game-id',
        channel_messages=[game_post_1, game_post_2]
    )

    games_repository = FakeGamesRepository([game])
    discord_messaging = FakeDiscordMessaging()

    game_post_manager = _game_post_manager(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )

    # When
    await game_post_manager.update(game)

    # Then
    update_channel_message_calls = discord_messaging.updated_channel_messages
    assert len(update_channel_message_calls) == 2
    assert {
               'channel_id': game_post_1.channel_id,
               'message_id': game_post_1.message_id,
               'embed': post_embed,
           } in update_channel_message_calls
    assert {
               'channel_id': game_post_2.channel_id,
               'message_id': game_post_2.message_id,
               'embed': post_embed,
           } in update_channel_message_calls


async def test_guess_channel_message_gone_silently_fails():
    # Given
    guild_id = 1001
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

    game_post_manager = _game_post_manager(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
    )

    # When
    await game_post_manager.update(game)

    # Then that channel message is removed from the game
    updated_game = games_repository.get(guild_id=guild_id, game_id=game_id)
    assert len(updated_game.channel_messages) == 1
    assert updated_game.channel_messages[0].message_id == other_channel_message.message_id


def _game_post_manager(games_repository=None, message_provider=None, discord_messaging=None):
    if games_repository is None:
        games_repository = FakeGamesRepository()

    if message_provider is None:
        message_provider = MagicMock(MessageProvider)

    if discord_messaging is None:
        discord_messaging = FakeDiscordMessaging()

    return GamePostManagerImpl(
        games_repository=games_repository,
        message_provider=message_provider,
        discord_messaging=discord_messaging,
    )
