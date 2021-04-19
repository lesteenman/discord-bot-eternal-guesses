import typing
from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.add_management_role import AddManagementRoleRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeConfigsRepository

pytestmark = pytest.mark.asyncio


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

    message = "Management role added"
    message_provider = MagicMock(MessageProvider)
    message_provider.added_management_role.return_value = message

    route = AddManagementRoleRoute(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert role in guild_config.management_roles

    assert response.is_ephemeral
    assert response.content == message


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

    message = "Role is already a management role."
    message_provider = MagicMock(MessageProvider)
    message_provider.add_duplicate_management_role.return_value = message

    route = AddManagementRoleRoute(
        configs_repository=configs_repository,
        message_provider=message_provider,
    )

    # When
    response = await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert duplicate_role in guild_config.management_roles
    assert len(guild_config.management_roles) == 1

    assert response.is_ephemeral
    assert response.content == message


def _make_event(guild_id: int = -1, options: typing.Dict = None) -> DiscordEvent:
    if options is None:
        options = {}

    return DiscordEvent(
        command=DiscordCommand(
            command_id=-1,
            command_name="admin",
            subcommand_name="does-not-matter",
            options=options
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
