import json
from unittest.mock import patch

import pytest
from eternal_guesses import router
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, CommandType, DiscordMember
from eternal_guesses.model.discord_response import DiscordResponse

pytestmark = pytest.mark.asyncio


@patch.object(router.routes.ping, 'call', autospec=True)
async def test_handle_ping(mock_route):
    # Given
    event = DiscordEvent()
    event.type = CommandType.PING

    pong_response = DiscordResponse.pong()
    mock_route.return_value = pong_response

    # When
    response = await router.route(event)

    # Then
    assert response.status_code == 200
    assert json.loads(response.body) == pong_response.json()


@patch.object(router.routes.guess, 'call', autospec=True)
async def test_handle_guess(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "guess"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    guess_response = DiscordResponse.acknowledge()
    mock_route.return_value = guess_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == guess_response.json()


@patch.object(router.routes.manage, 'post', autospec=True)
async def test_handle_manage_post(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "manage"
    command.subcommand_name = "post"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.manage, 'close', autospec=True)
async def test_handle_manage_close(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "manage"
    command.subcommand_name = "close"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.manage, 'list_games', autospec=True)
async def test_handle_manage_list(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "manage"
    command.subcommand_name = "list-games"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.create, 'call', autospec=True)
async def test_handle_create(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "create"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.admin, 'info', autospec=True)
async def test_handle_admin_info(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "info"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.admin, 'add_management_channel', autospec=True)
async def test_handle_admin_add_management_channel(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "add-management-channel"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.admin, 'remove_management_channel', autospec=True)
async def test_handle_admin_remove_management_channel(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "remove-management-channel"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.admin, 'add_management_role', autospec=True)
async def test_handle_admin_add_management_role(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "add-management-role"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


@patch.object(router.routes.admin, 'remove_management_role', autospec=True)
async def test_handle_admin_remove_management_role(mock_route):
    # Given
    command = DiscordCommand()
    command.command_name = "admin"
    command.subcommand_name = "remove-management-role"

    event = DiscordEvent()
    event.type = CommandType.COMMAND
    event.command = command
    event.member = DiscordMember()

    mock_response = DiscordResponse.acknowledge()
    mock_route.return_value = mock_response

    # When
    response = await router.route(event)

    # Then
    mock_route.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()
