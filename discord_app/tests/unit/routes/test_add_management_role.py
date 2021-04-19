import typing

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.error.discord_event_disallowed_error import DiscordEventDisallowedError
from eternal_guesses.routes.add_management_role import AddManagementRoleRoute
from tests.fakes import FakeConfigsRepository, FakeMessageProvider, FakeCommandAuthorizer, FakeDiscordMessaging

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

    route = AddManagementRoleRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(admin=True),
        discord_messaging=FakeDiscordMessaging(),
    )

    # When
    await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert role in guild_config.management_roles


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

    route = AddManagementRoleRoute(
        configs_repository=configs_repository,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(admin=True),
        discord_messaging=FakeDiscordMessaging(),
    )

    # When
    await route.call(event)

    # Then
    guild_config = configs_repository.get(guild_id)
    assert duplicate_role in guild_config.management_roles
    assert len(guild_config.management_roles) == 1


async def test_admin_add_management_role_unauthorized():
    # Given: the command authorizer fails
    authorizer = FakeCommandAuthorizer(admin=False)
    event = _make_event()

    route = AddManagementRoleRoute(
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
            subcommand_name="does-not-matter",
            options=options
        ),
        guild_id=guild_id,
        member=DiscordMember()
    )
