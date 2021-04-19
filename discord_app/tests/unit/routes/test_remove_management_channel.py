import typing

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.remove_management_channel import RemoveManagementChannelRoute
from tests.fakes import FakeConfigsRepository, FakeMessageProvider

pytestmark = pytest.mark.asyncio


async def test_remove_management_channel():
    # Given
    guild_id = 1001
    management_channel = 9500

    # We have a management channel
    configs_repository = FakeConfigsRepository(guild_id=guild_id, management_channels=[management_channel])

    # And we remove it
    event = _make_event(
        guild_id=guild_id,
        options={
            'channel': management_channel
        },
    )

    route = RemoveManagementChannelRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert management_channel not in guild_config.management_channels

    assert response.is_ephemeral


async def test_remove_invalid_management_channel():
    # Given
    guild_id = 1001
    channel_to_remove = 9500
    other_channel = 9510

    # We have a management channel
    configs_repository = FakeConfigsRepository(guild_id=guild_id, management_channels=[other_channel])

    # And we try to remove a channel that's not a management channel
    event = _make_event(
        guild_id=guild_id,
        options={
            'channel': channel_to_remove
        }
    )

    route = RemoveManagementChannelRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert channel_to_remove not in guild_config.management_channels
    assert other_channel in guild_config.management_channels

    assert response.is_ephemeral


def _make_event(guild_id: int = -1, options: typing.Dict = None) -> DiscordEvent:
    if options is None:
        options = {}

    return DiscordEvent(
        command=DiscordCommand(
            command_id=-1,
            command_name="admin",
            subcommand_name="remove-management-channel",
            options=options
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )