from typing import List

import pytest

from eternal_guesses.authorization.command_authorizer import CommandAuthorizerImpl
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord_event import DiscordEvent, CommandType
from eternal_guesses.model.discord_member import DiscordMember
from eternal_guesses.repositories.configs_repository import ConfigsRepository

pytestmark = pytest.mark.asyncio


class FakeConfigsRepository(ConfigsRepository):
    def __init__(self, guild_id: int, management_channels: List[int] = None, management_roles: List[int] = None):
        if management_channels is None:
            management_channels = []

        if management_roles is None:
            management_roles = []

        self.management_channels = management_channels
        self.management_roles = management_roles

        self.guild_config = GuildConfig(
            guild_id=guild_id,
            management_channels=self.management_channels,
            management_roles=self.management_roles
        )

    def get(self, guild_id: int) -> GuildConfig:
        if guild_id == self.guild_config.guild_id:
            return self.guild_config


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
        command_type=CommandType.COMMAND,
        channel_id=other_channel,
        member=DiscordMember(roles=[other_role]),
    )

    # Then
    try:
        await command_authorizer.authorize_management_call(event=event)
        assert False
    except DiscordEventDisallowedError:
        pass


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
        command_type=CommandType.COMMAND,
        channel_id=other_channel,
        member=DiscordMember(roles=[management_role]),
    )

    # Then
    await command_authorizer.authorize_management_call(event=event)


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
        command_type=CommandType.COMMAND,
        channel_id=management_channel,
        member=DiscordMember(roles=[other_role]),
    )

    # Then
    await command_authorizer.authorize_management_call(event=event)
