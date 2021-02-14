import json
from unittest.mock import AsyncMock

import pytest

from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, CommandType, DiscordMember
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.router import RouterImpl
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.routes.ping import PingRoute

pytestmark = pytest.mark.asyncio


async def test_handle_ping():
    # Given
    event = DiscordEvent()
    event.type = CommandType.PING

    pong_response = DiscordResponse.pong()

    mock_ping_route = AsyncMock(PingRoute, autospec=True)
    mock_ping_route.call.return_value = pong_response

    # When
    router = RouterImpl(ping_route=mock_ping_route)
    response = await router.route(event)

    # Then
    assert response.status_code == 200
    assert json.loads(response.body) == pong_response.json()


async def test_handle_guess():
    # Given
    command = DiscordCommand()
    command.command_name = "guess"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    guess_response = DiscordResponse.acknowledge()

    mock_guess_route = AsyncMock(GuessRoute, autospec=True)
    mock_guess_route.call.return_value = guess_response

    # When
    router = RouterImpl(guess_route=mock_guess_route)
    response = await router.route(event)

    # Then
    mock_guess_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == guess_response.json()


async def test_handle_manage_post():
    # Given
    command = DiscordCommand()
    command.command_name = "manage"
    command.subcommand_name = "post"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_manage_route = AsyncMock(ManageRoute, autospec=True)
    mock_manage_route.post.return_value = mock_response

    # When
    router = RouterImpl(manage_route=mock_manage_route)
    response = await router.route(event)

    # Then
    mock_manage_route.post.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_manage_close():
    # Given
    command = DiscordCommand()
    command.command_name = "manage"
    command.subcommand_name = "close"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_manage_route = AsyncMock(ManageRoute, autospec=True)
    mock_manage_route.close.return_value = mock_response

    # When
    router = RouterImpl(manage_route=mock_manage_route)
    response = await router.route(event)

    # Then
    mock_manage_route.close.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_manage_list():
    # Given
    command = DiscordCommand()
    command.command_name = "manage"
    command.subcommand_name = "list-games"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_manage_route = AsyncMock(ManageRoute, autospec=True)
    mock_manage_route.list_games.return_value = mock_response

    # When
    router = RouterImpl(manage_route=mock_manage_route)
    response = await router.route(event)

    # Then
    mock_manage_route.list_games.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_create():
    # Given
    command = DiscordCommand()
    command.command_name = "create"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_create_route = AsyncMock(CreateRoute, autospec=True)
    mock_create_route.call.return_value = mock_response

    # When
    router = RouterImpl(create_route=mock_create_route)
    response = await router.route(event)

    # Then
    mock_create_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_info():
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "info"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_admin_route = AsyncMock(AdminRoute, autospec=True)
    mock_admin_route.info.return_value = mock_response

    # When
    router = RouterImpl(admin_route=mock_admin_route)
    response = await router.route(event)

    # Then
    mock_admin_route.info.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_add_management_channel():
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "add-management-channel"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_admin_route = AsyncMock(AdminRoute, autospec=True)
    mock_admin_route.add_management_channel.return_value = mock_response

    # When
    router = RouterImpl(admin_route=mock_admin_route)
    response = await router.route(event)

    # Then
    mock_admin_route.add_management_channel.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_remove_management_channel():
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "remove-management-channel"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_admin_route = AsyncMock(AdminRoute, autospec=True)
    mock_admin_route.remove_management_channel.return_value = mock_response

    # When
    router = RouterImpl(admin_route=mock_admin_route)
    response = await router.route(event)

    # Then
    mock_admin_route.remove_management_channel.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_add_management_role():
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "add-management-role"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_admin_route = AsyncMock(AdminRoute, autospec=True)
    mock_admin_route.add_management_role.return_value = mock_response

    # When
    router = RouterImpl(admin_route=mock_admin_route)
    response = await router.route(event)

    # Then
    mock_admin_route.add_management_role.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_remove_management_role():
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "remove-management-role"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()

    mock_admin_route = AsyncMock(AdminRoute, autospec=True)
    mock_admin_route.remove_management_role.return_value = mock_response

    # When
    router = RouterImpl(admin_route=mock_admin_route)
    response = await router.route(event)

    # Then
    mock_admin_route.remove_management_role.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()
