from typing import Dict

import pytest

from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord_event import DiscordEvent, CommandType, DiscordCommand
from eternal_guesses.model.discord_member import DiscordMember
from eternal_guesses.model.discord_response import ResponseType
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeCommandAuthorizer, FakeConfigsRepository

pytestmark = pytest.mark.asyncio


class FakeMessageProvider(MessageProvider):
    def __init__(self):
        self.message = None
        self.expected_config = None

    def expect_channel_admin_info_call(self, expected_config: GuildConfig, message: str):
        self.expected_config = expected_config
        self.message = message

    def channel_admin_info(self, config: GuildConfig) -> str:
        if config == self.expected_config:
            return self.message


async def test_admin_info():
    # Given
    guild_id = 1001

    configs_repository = FakeConfigsRepository(guild_id=guild_id)
    command_authorizer = FakeCommandAuthorizer(passes=True)

    guild_config = configs_repository.get(guild_id)

    static_message = "admin-info"
    message_provider = FakeMessageProvider()
    message_provider.expect_channel_admin_info_call(expected_config=guild_config, message=static_message)

    route = AdminRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
        command_authorizer=command_authorizer
    )

    event = _make_event(guild_id=guild_id)

    # When
    response = await route.info(event)

    # Then
    assert response.content == static_message
    assert response.response_type == ResponseType.CHANNEL_MESSAGE_WITH_SOURCE


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

    route = AdminRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.add_management_channel(event)

    # Then
    config = configs_repository.get(guild_id)
    assert channel in config.management_channels


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

    route = AdminRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.add_management_channel(event)

    # Then
    config = configs_repository.get(guild_id)
    assert channel in config.management_channels
    assert len(config.management_channels) == 1


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

    route = AdminRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.remove_management_channel(event)

    # Then
    config = configs_repository.get(guild_id)
    assert management_channel not in config.management_channels


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

    route = AdminRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.remove_management_channel(event)

    # Then
    config = configs_repository.get(guild_id)
    assert channel_to_remove not in config.management_channels
    assert other_channel in config.management_channels


async def test_add_management_role():
    # Given
    guild_id = 1001
    role = 6000

    # We have no management roles
    configs_repository = FakeConfigsRepository(guild_id=guild_id)

    # And we add a new management role
    event = _make_event(
        guild_id=guild_id,
        options={'role': role}
    )

    route = AdminRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.add_management_role(event)

    # Then
    config = configs_repository.get(guild_id)
    assert role in config.management_roles


async def test_add_duplicate_management_role():
    # Given
    guild_id = 1001
    duplicate_role = 6000

    # The role is already a management role
    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_roles=[duplicate_role]
    )

    # And we try to add it again
    event = _make_event(
        guild_id=guild_id,
        options={'role': duplicate_role, }
    )

    route = AdminRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.add_management_role(event)

    # Then
    config = configs_repository.get(guild_id)
    assert duplicate_role in config.management_roles
    assert len(config.management_roles) == 1


async def test_remove_management_role():
    # Given
    guild_id = 1001
    role = 6050

    # The role is a management_role
    configs_repository = FakeConfigsRepository(guild_id=guild_id, management_roles=[role])

    # And we remove it
    event = _make_event(
        guild_id=guild_id,
        options={'role': role}
    )

    route = AdminRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.remove_management_role(event)

    # Then
    config = configs_repository.get(guild_id)
    assert role not in config.management_roles


async def test_remove_invalid_management_role():
    # Given
    guild_id = 1001
    management_role = 6060
    role_to_remove = 6050

    # We have a management role
    configs_repository = FakeConfigsRepository(guild_id=guild_id, management_roles=[management_role])

    # And we remove another role
    event = _make_event(
        guild_id=guild_id,
        options={'role': role_to_remove}
    )

    route = AdminRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    await route.remove_management_role(event)

    # Then
    config = configs_repository.get(guild_id)
    assert role_to_remove not in config.management_roles
    assert management_role in config.management_roles


async def test_admin_info_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(passes=False)
    event = _make_event()

    route = AdminRoute(
        command_authorizer=authorizer,
        message_provider=FakeMessageProvider(),
        configs_repository=FakeConfigsRepository(guild_id=-1)
    )

    # Then: the call should raise an Exception
    try:
        await route.info(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_admin_add_management_channel_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(passes=False)
    event = _make_event()

    route = AdminRoute(
        command_authorizer=authorizer,
        message_provider=FakeMessageProvider(),
        configs_repository=FakeConfigsRepository(guild_id=-1)
    )

    # Then: the call should raise an Exception
    try:
        await route.add_management_channel(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_admin_remove_management_channel_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(passes=False)
    event = _make_event()

    route = AdminRoute(
        command_authorizer=authorizer,
        message_provider=FakeMessageProvider(),
        configs_repository=FakeConfigsRepository(guild_id=-1)
    )

    # Then: the call should raise an Exception
    try:
        await route.remove_management_channel(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_admin_add_management_role_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(passes=False)
    event = _make_event()

    route = AdminRoute(
        command_authorizer=authorizer,
        message_provider=FakeMessageProvider(),
        configs_repository=FakeConfigsRepository(guild_id=-1)
    )

    # Then: the call should raise an Exception
    try:
        await route.add_management_role(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_admin_remove_management_role_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(passes=False)
    event = _make_event()

    route = AdminRoute(
        command_authorizer=authorizer,
        message_provider=FakeMessageProvider(),
        configs_repository=FakeConfigsRepository(guild_id=-1)
    )

    # Then: the call should raise an Exception
    try:
        await route.remove_management_role(event)
        assert False
    except DiscordEventDisallowedError:
        pass


def _make_event(guild_id: int = -1, options: Dict = None) -> DiscordEvent:
    if options is None:
        options = {}

    return DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="admin",
            subcommand_name="does-not-matter",
            options=options
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
