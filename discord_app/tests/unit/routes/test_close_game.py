from typing import Dict
from unittest.mock import MagicMock

import discord
import pytest

from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_event import DiscordEvent, DiscordCommand
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.close_game import CloseGameRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeDiscordMessaging, FakeGamesRepository

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

    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game.game_id,
        }
    )

    game_closed_message = "Game closed."
    message_provider = MagicMock(MessageProvider)
    message_provider.game_closed.return_value = game_closed_message

    discord_messaging = FakeDiscordMessaging()
    route = CloseGameRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )

    # When we close it
    response = await route.call(event)

    # Then it should be closed
    saved_game = games_repository.get(guild_id, game.game_id)
    assert saved_game.closed

    assert response.is_ephemeral
    assert response.content == game_closed_message


async def test_close_updates_channel_messages():
    guild_id = 1007
    game_id = 'game-id-1'

    # We have an open game with channel messages
    channel_message_1 = ChannelMessage(channel_id=1, message_id=10)
    channel_message_2 = ChannelMessage(channel_id=2, message_id=11)
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=False,
        channel_messages=[channel_message_1, channel_message_2]
    )
    games_repository = FakeGamesRepository([game])

    post_embed = discord.Embed()
    message_provider = MagicMock(MessageProvider)
    message_provider.game_post_embed.return_value = post_embed

    discord_messaging = FakeDiscordMessaging()
    route = CloseGameRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )

    # When we close it
    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game.game_id,
        }
    )
    await route.call(event)

    # Then the channel messages are updated
    assert len(discord_messaging.updated_channel_messages) == 2

    # Both messages should not have a view (no buttons)
    assert {
               'channel_id': channel_message_1.channel_id,
               'message_id': channel_message_1.message_id,
               'embed': post_embed,
           } in discord_messaging.updated_channel_messages

    assert {
               'channel_id': channel_message_2.channel_id,
               'message_id': channel_message_2.message_id,
               'embed': post_embed,
           } in discord_messaging.updated_channel_messages


async def test_close_already_closed_game():
    # Given
    guild_id = 1007
    game_id = 'game-id-1'

    # We have a closed game
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=True
    )
    games_repository = FakeGamesRepository([game])

    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game.game_id,
        }
    )

    game_already_closed_message = "Game was already closed closed."
    message_provider = MagicMock(MessageProvider)
    message_provider.game_closed.return_value = game_already_closed_message

    route = CloseGameRoute(
        games_repository=games_repository,
        discord_messaging=FakeDiscordMessaging(),
        message_provider=message_provider,
    )

    # When we close it again
    response = await route.call(event)

    # Then it should just still be closed
    saved_game = games_repository.get(guild_id, game.game_id)
    assert saved_game.closed

    assert response.is_ephemeral
    assert response.content == game_already_closed_message


def _make_event(guild_id: int = -1, options: Dict = None, discord_member: DiscordMember = None, channel_id: int = -1):
    if options is None:
        options = {}

    if discord_member is None:
        discord_member = DiscordMember()

    return DiscordEvent(
        guild_id=guild_id,
        channel_id=channel_id,
        command=DiscordCommand(
            command_name="manage",
            subcommand_name="close",
            options=options,
        ),
        member=discord_member
    )
