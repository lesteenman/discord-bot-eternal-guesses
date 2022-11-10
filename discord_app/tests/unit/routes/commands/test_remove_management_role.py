import typing

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.remove_management_role import \
    RemoveManagementRoleRoute
from tests.fakes import FakeConfigsRepository, FakeMessageProvider

pytestmark = pytest.mark.asyncio


async def test_remove_management_role():
    # Given
    guild_id = 1001
    role = 6050

    # The role is a management_role
    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_roles=[role]
    )

    # And we remove it
    event = _make_event(
        guild_id=guild_id,
        options={
            'role': role
        }
    )

    route = RemoveManagementRoleRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert role not in guild_config.management_roles

    assert response.is_ephemeral


async def test_remove_invalid_management_role():
    # Given
    guild_id = 1001
    management_role = 6060
    role_to_remove = 6050

    # We have a management role
    configs_repository = FakeConfigsRepository(
        guild_id=guild_id,
        management_roles=[management_role]
    )

    # And we remove another role
    event = _make_event(
        guild_id=guild_id,
        options={
            'role': role_to_remove
        }
    )

    route = RemoveManagementRoleRoute(
        message_provider=FakeMessageProvider(),
        configs_repository=configs_repository,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert role_to_remove not in guild_config.management_roles
    assert management_role in guild_config.management_roles

    assert response.is_ephemeral


def _make_event(
    guild_id: int = -1,
    options: typing.Dict = None
) -> DiscordEvent:
    if options is None:
        options = {}

    return DiscordEvent(
        command=DiscordCommand(
            command_name="admin",
            subcommand_name="remove-management-role",
            options=options
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
