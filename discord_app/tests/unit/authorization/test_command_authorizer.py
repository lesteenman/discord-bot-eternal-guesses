import pytest

from eternal_guesses.authorization.command_authorizer import CommandAuthorizerImpl
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from tests.fakes import FakeConfigsRepository

pytestmark = pytest.mark.asyncio


async def test_unauthorized_management_call():
    # Given
    guild_id = 1000
    management_role = 2000
    other_role = 2001
    management_channel = 3000
    other_channel = 3001

    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_channels=[management_channel],
        management_roles=[management_role]
    )

    command_authorizer = CommandAuthorizerImpl(configs_repository=configs_repository)

    event = DiscordEvent(
        guild_id=guild_id,
        channel_id=other_channel,
        member=DiscordMember(roles=[other_role]),
    )

    # When
    allowed = await command_authorizer.authorize_management_call(event=event)

    # Then
    assert not allowed


async def test_authorized_role_management_call():
    # Given
    guild_id = 1000
    management_role = 2000
    management_channel = 3000
    other_channel = 3001

    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_channels=[management_channel],
        management_roles=[management_role]
    )

    command_authorizer = CommandAuthorizerImpl(configs_repository=configs_repository)

    event = DiscordEvent(
        guild_id=guild_id,
        channel_id=other_channel,
        member=DiscordMember(roles=[management_role]),
    )

    # When
    allowed = await command_authorizer.authorize_management_call(event=event)

    # Then
    assert allowed


async def test_authorized_channel_management_call():
    # Given
    guild_id = 1000
    management_role = 2000
    other_role = 2001
    management_channel = 3000

    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_channels=[management_channel],
        management_roles=[management_role]
    )

    command_authorizer = CommandAuthorizerImpl(configs_repository=configs_repository)

    event = DiscordEvent(
        guild_id=guild_id,
        channel_id=management_channel,
        member=DiscordMember(roles=[other_role]),
    )

    # When
    allowed = await command_authorizer.authorize_management_call(event=event)

    # Then
    assert allowed


async def test_admin_management_call():
    # Given
    guild_id = 1000
    management_role = 2000
    other_role = 2001
    management_channel = 3000
    other_channel = 3001

    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_channels=[management_channel],
        management_roles=[management_role]
    )

    command_authorizer = CommandAuthorizerImpl(configs_repository=configs_repository)

    event = DiscordEvent(
        guild_id=guild_id,
        channel_id=other_channel,
        member=DiscordMember(
            roles=[other_role],
            is_admin=True
        ),
    )

    # When
    allowed = await command_authorizer.authorize_management_call(event=event)

    # Then
    assert allowed


async def test_unauthorized_admin_call():
    # Given
    guild_id = 1000

    command_authorizer = CommandAuthorizerImpl(configs_repository=FakeConfigsRepository(guild_id))

    event = DiscordEvent(
        guild_id=guild_id,
        member=DiscordMember(),
    )

    # When
    allowed = await command_authorizer.authorize_admin_call(event=event)

    # Then
    assert not allowed


async def test_authorized_admin_call():
    # Given
    guild_id = 1000

    command_authorizer = CommandAuthorizerImpl(configs_repository=FakeConfigsRepository(guild_id))

    event = DiscordEvent(
        guild_id=guild_id,
        member=DiscordMember(is_admin=True),
    )

    # When
    allowed = await command_authorizer.authorize_admin_call(event=event)

    # Then
    assert allowed
