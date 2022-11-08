from unittest.mock import AsyncMock, MagicMock

import aiohttp
import discord
import pytest

from eternal_guesses.api.permission_set import PermissionSet
from eternal_guesses.api.route_definition import RouteDefinition, \
    ApplicationCommandDefinition
from eternal_guesses.api.route_handler import RouteHandlerImpl
from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse, \
    ResponseType
from eternal_guesses.routes.route import Route
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeCommandAuthorizer

pytestmark = pytest.mark.asyncio


async def test_handle():
    # Given
    route_handler = _route_handler()

    event = DiscordEvent(
        command=DiscordCommand(
            command_name="ping",
        )
    )

    response = DiscordResponse.ephemeral_channel_message("You handled it very well!")

    mock_route = AsyncMock(Route)
    mock_route.call.return_value = response

    route_definition = ApplicationCommandDefinition(
        route=mock_route,
        command="ping",
    )

    # When
    response = await route_handler.handle(event, route_definition)

    # Then
    assert response == response


async def test_handle_disallowed_management_call():
    # Given
    message = "Command 'create' can only be used by management users."

    command_authorizer = FakeCommandAuthorizer(management=False)

    message_provider = MagicMock(MessageProvider)
    message_provider.disallowed_management_call.return_value = message

    route_handler = _route_handler(
        command_authorizer=command_authorizer,
        message_provider=message_provider,
    )

    event = DiscordEvent()
    route_definition = ApplicationCommandDefinition(
        route=AsyncMock(Route),
        command="create",
        permission=PermissionSet.MANAGEMENT,
    )

    # When
    response = await route_handler.handle(event, route_definition)

    # Then
    assert response.response_type == ResponseType.CHANNEL_MESSAGE
    assert response.is_ephemeral
    assert response.content == message


async def test_handle_disallowed_admin_call():
    # Given
    message = "Command '/eternal-guess admin info' can only be used by admin users."

    command_authorizer = FakeCommandAuthorizer(admin=False)

    message_provider = MagicMock(MessageProvider)
    message_provider.disallowed_admin_call.return_value = message

    route_handler = _route_handler(
        command_authorizer=command_authorizer,
        message_provider=message_provider,
    )

    event = DiscordEvent()
    route_definition = ApplicationCommandDefinition(
        route=AsyncMock(Route),
        command="admin",
        subcommand="info",
        permission=PermissionSet.ADMIN,
    )

    # When
    response = await route_handler.handle(event, route_definition)

    # Then
    assert response.response_type == ResponseType.CHANNEL_MESSAGE
    assert response.is_ephemeral
    assert response.content == message


async def test_handle_raised_forbidden():
    # Given
    clientside_error_message = "The bot has insufficient permissions to do this."

    message_provider = MagicMock(MessageProvider)
    message_provider.bot_missing_access.return_value = clientside_error_message

    route_handler = _route_handler(message_provider=message_provider)

    event = DiscordEvent(
        command=DiscordCommand(
            command_name="ping",
        )
    )

    mock_route = AsyncMock(Route)
    mock_route.call.side_effect = discord.Forbidden(
        MagicMock(aiohttp.ClientResponse),
        "Missing Access."
    )

    route_definition = ApplicationCommandDefinition(
        route=mock_route,
        command="ping",
    )

    # When
    response = await route_handler.handle(event, route_definition)

    # Then
    assert response.is_ephemeral
    assert response.content == clientside_error_message


def _route_handler(command_authorizer: CommandAuthorizer = None,
                   message_provider: MessageProvider = None):
    if command_authorizer is None:
        command_authorizer = FakeCommandAuthorizer()

    if message_provider is None:
        message_provider = MessageProvider()

    return RouteHandlerImpl(
        command_authorizer=command_authorizer,
        message_provider=message_provider,
    )
