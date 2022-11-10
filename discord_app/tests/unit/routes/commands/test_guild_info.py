import typing

import pytest

from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.guild_info import GuildInfoRoute
from tests.fakes import FakeMessageProvider, FakeConfigsRepository

pytestmark = pytest.mark.asyncio


async def test_admin_info():
    # Given
    guild_id = 1001

    configs_repository = FakeConfigsRepository(guild_id=guild_id)

    guild_config = configs_repository.get(guild_id)

    static_message = "admin-info"
    message_provider = FakeMessageProvider()
    message_provider.expect_channel_admin_info_call(
        expected_config=guild_config,
        message=static_message
    )

    route = GuildInfoRoute(
        message_provider=message_provider,
        configs_repository=configs_repository,
    )

    event = _make_event(guild_id=guild_id)

    # When
    response = await route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == static_message


def _make_event(
    guild_id: int = -1,
    options: typing.Dict = None
) -> DiscordEvent:
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
