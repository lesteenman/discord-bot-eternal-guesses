import typing

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.error.discord_event_disallowed_error import DiscordEventDisallowedError
from eternal_guesses.routes.add_management_channel import AddManagementChannelRoute
from tests.fakes import FakeConfigsRepository, FakeMessageProvider, FakeCommandAuthorizer, FakeDiscordMessaging

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

    route = AddManagementChannelRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(admin=True),
        discord_messaging=FakeDiscordMessaging(),
    )

    # When
    await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert channel in guild_config.management_channels
    assert len(guild_config.management_channels) == 1


async def test_add_management_channel():
    # Given
    guild_id = 1001
    channel = 9500

    # We have no management channels yet
    configs_repository = FakeConfigsRepository(guild_id=guild_id)

    # We add the new management channel
    event = _make_event(
        guild_id=guild_id,
        options={'channel': channel},
    )

    route = AddManagementChannelRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
        command_authorizer=FakeCommandAuthorizer(admin=True),
        discord_messaging=FakeDiscordMessaging(),
    )

    # When
    await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert channel in guild_config.management_channels


async def test_admin_add_management_channel_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(admin=False)
    event = _make_event()

    route = AddManagementChannelRoute(
        command_authorizer=authorizer,
        message_provider=FakeMessageProvider(),
        configs_repository=FakeConfigsRepository(guild_id=-1),
        discord_messaging=FakeDiscordMessaging(),
    )

    # Then: the call should raise an Exception
    try:
        await route.call(event)
        assert False
    except DiscordEventDisallowedError:
        pass


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
