import typing
from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.add_management_channel import AddManagementChannelRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeConfigsRepository

pytestmark = pytest.mark.asyncio


async def test_add_duplicate_management_channel():
    # Given
    guild_id = 1001
    channel = 9500

    # We have a channel that's a management channel
    configs_repository = FakeConfigsRepository(guild_id=guild_id, management_channels=[channel])

    # And we try to add it again
    event = _make_event(
        guild_id=guild_id,
        options={
            'channel': channel
        }
    )

    error_message = "channel is already a management channel."

    message_provider = MagicMock(MessageProvider)
    message_provider.error_duplicate_management_channel.return_value = error_message

    route = AddManagementChannelRoute(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert channel in guild_config.management_channels
    assert len(guild_config.management_channels) == 1

    assert response.is_ephemeral
    assert response.content == error_message


async def test_add_management_channel():
    # Given
    guild_id = 1001
    channel = 9500

    # We have no management channels yet
    configs_repository = FakeConfigsRepository(guild_id=guild_id)

    message = "New management channel added."
    message_provider = MagicMock(MessageProvider)
    message_provider.added_management_channel.return_value = message

    # We add the new management channel
    event = _make_event(
        guild_id=guild_id,
        options={'channel': channel},
    )

    route = AddManagementChannelRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert channel in guild_config.management_channels

    assert response.is_ephemeral
    assert response.content == message


def _make_event(guild_id: int = -1, options: typing.Dict = None) -> DiscordEvent:
    if options is None:
        options = {}

    return DiscordEvent(
        command=DiscordCommand(
            command_id=-1,
            command_name="admin",
            subcommand_name="add-management-channel",
            options=options
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
