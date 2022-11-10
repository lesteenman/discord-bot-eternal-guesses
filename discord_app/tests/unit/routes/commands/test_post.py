import typing
from unittest.mock import MagicMock

import discord
import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.post import PostRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository, FakeDiscordMessaging, \
    FakeMessageProvider

pytestmark = pytest.mark.asyncio


async def test_post_creates_channel_message():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    # We have a game
    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    # And we have a mock message provider
    post_embed = discord.Embed()
    post_view = discord.ui.View()
    message_provider = MagicMock(MessageProvider)
    message_provider.game_post_embed.return_value = post_embed
    message_provider.game_post_view.return_value = post_view

    discord_messaging = FakeDiscordMessaging()
    post_route = PostRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )

    # When we post a channel message for our game with an explicit channel
    event = _make_event(guild_id=guild_id, options={
        'game-id': game_id,
        'channel': channel_id,
    })
    await post_route.call(event)

    # Then a message about that game is posted in the given channel
    assert {
               'channel_id': channel_id,
               'embed': post_embed,
               'view': post_view
           } in discord_messaging.sent_channel_messages

    # And the channel id is saved in the game
    saved_game = games_repository.get(guild_id, game_id)
    assert len(saved_game.channel_messages) == 1


async def test_post_without_channel_uses_event_channel():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    event_channel_id = 50001

    # We have a game
    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    post_embed = discord.Embed()
    post_view = discord.ui.View()
    message_provider = MagicMock(MessageProvider)
    message_provider.game_post_embed.return_value = post_embed
    message_provider.game_post_view.return_value = post_view

    discord_messaging = FakeDiscordMessaging()

    post_route = PostRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )

    # When we post a channel message without an explicit target channel
    event = _make_event(guild_id=guild_id,
                        channel_id=event_channel_id,
                        options={'game-id': game_id})
    await post_route.call(event)

    # Then a message for that game is posted in the channel we sent this command from
    assert {
               'channel_id': event_channel_id,
               'embed': post_embed,
               'view': post_view,
           } in discord_messaging.sent_channel_messages


async def test_post_saves_message_id_to_game():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    new_message_id = 1000
    discord_messaging = FakeDiscordMessaging()
    discord_messaging.created_channel_message_id = 1000

    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    post_route = PostRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=FakeMessageProvider(),
    )

    # When
    event = _make_event(guild_id=guild_id, options={
        'game-id': game_id,
        'channel': channel_id,
    })
    await post_route.call(event)

    # Then
    updated_game = games_repository.get(guild_id, game_id)
    assert updated_game.channel_messages is not None

    assert any(channel_message.channel_id == channel_id and channel_message.message_id == new_message_id
               for channel_message in updated_game.channel_messages)


async def test_post_invalid_game_id_sends_dm_error():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001
    event_channel_id = 7733

    # We have no games
    games_repository = FakeGamesRepository([])
    discord_messaging = FakeDiscordMessaging()

    formatted_error = "mock formatted error"
    message_provider = MagicMock(MessageProvider)
    message_provider.error_game_not_found.return_value = formatted_error

    post_route = PostRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
    )

    discord_member = DiscordMember()

    # When
    event = _make_event(
        guild_id=guild_id,
        discord_member=discord_member,
        channel_id=event_channel_id,
        options={
            'game-id': game_id,
            'channel': channel_id,
        }
    )
    response = await post_route.call(event)

    # Then
    message_provider.error_game_not_found.assert_called_with(game_id)

    assert response.is_ephemeral
    assert response.content == formatted_error


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
            subcommand_name="post",
            options=options,
        ),
        member=discord_member
    )
