import pytest

from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord_event import DiscordEvent, CommandType, DiscordCommand
from eternal_guesses.model.discord_member import DiscordMember
from eternal_guesses.model.discord_response import ResponseType
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeCommandAuthorizer
from tests.unit.authorization.test_command_authorizer import FakeConfigsRepository

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

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        command=DiscordCommand(
            command_id="-1",
            command_name="admin",
            subcommand_name="info",
        ),
        guild_id=guild_id,
        member=DiscordMember(
            user_id=1,
            is_admin=True
        )
    )

    # When
    response = await route.info(event)

    # Then
    assert response.content == static_message
    assert response.response_type == ResponseType.CHANNEL_MESSAGE_WITH_SOURCE
