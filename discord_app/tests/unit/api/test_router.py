import json
from unittest.mock import AsyncMock

import pytest

from eternal_guesses.api.router import RouterImpl
from eternal_guesses.model.discord.discord_event import DiscordEvent, DiscordCommand
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.routes.add_management_channel import AddManagementChannelRoute
from eternal_guesses.routes.add_management_role import AddManagementRoleRoute
from eternal_guesses.routes.close_game import CloseGameRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.guild_info import GuildInfoRoute
from eternal_guesses.routes.list_games import ListGamesRoute
from eternal_guesses.routes.ping import PingRoute
from eternal_guesses.routes.post import PostRoute
from eternal_guesses.routes.remove_management_channel import RemoveManagementChannelRoute
from eternal_guesses.routes.remove_management_role import RemoveManagementRoleRoute
from eternal_guesses.routes.route import Route

pytestmark = pytest.mark.asyncio


async def test_handle_ping():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="ping",
        )
    )

    pong_response = DiscordResponse.pong()

    mock_ping_route = AsyncMock(PingRoute, autospec=True)
    mock_ping_route.call.return_value = pong_response

    # When
    router = _router(ping_route=mock_ping_route)
    response = await router.route(event)

    # Then
    assert response.status_code == 200
    assert json.loads(response.body) == pong_response.json()


async def test_handle_guess():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="guess"
        ),
        member=DiscordMember()
    )

    guess_response = DiscordResponse.acknowledge()

    mock_guess_route = AsyncMock(GuessRoute, autospec=True)
    mock_guess_route.call.return_value = guess_response

    # When
    router = _router(guess_route=mock_guess_route)
    response = await router.route(event)

    # Then
    mock_guess_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == guess_response.json()


async def test_handle_manage_post():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="manage",
            subcommand_name="post"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_post_route = AsyncMock(PostRoute, autospec=True)
    mock_post_route.call.return_value = mock_response

    # When
    router = _router(post_route=mock_post_route)
    response = await router.route(event)

    # Then
    mock_post_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_manage_close():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="manage",
            subcommand_name="close"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_close_game_route = AsyncMock(CloseGameRoute, autospec=True)
    mock_close_game_route.call.return_value = mock_response

    # When
    router = _router(close_game_route=mock_close_game_route)
    response = await router.route(event)

    # Then
    mock_close_game_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_manage_list():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="manage",
            subcommand_name="list-games"
        ),
        member=DiscordMember(),
    )

    mock_response = DiscordResponse.acknowledge()

    mock_list_games_route = AsyncMock(ListGamesRoute, autospec=True)
    mock_list_games_route.call.return_value = mock_response

    # When
    router = _router(list_games_route=mock_list_games_route)
    response = await router.route(event)

    # Then
    mock_list_games_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_create():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="create"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_create_route = AsyncMock(CreateRoute, autospec=True)
    mock_create_route.call.return_value = mock_response

    # When
    router = _router(create_route=mock_create_route)
    response = await router.route(event)

    # Then
    mock_create_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_info():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="admin",
            subcommand_name="info"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_guild_info_route = AsyncMock(GuildInfoRoute, autospec=True)
    mock_guild_info_route.call.return_value = mock_response

    # When
    router = _router(guild_info_route=mock_guild_info_route)
    response = await router.route(event)

    # Then
    mock_guild_info_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_add_management_channel():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="admin",
            subcommand_name="add-management-channel"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_add_management_channel_route = AsyncMock(AddManagementChannelRoute, autospec=True)
    mock_add_management_channel_route.call.return_value = mock_response

    # When
    router = _router(add_management_channel_route=mock_add_management_channel_route)
    response = await router.route(event)

    # Then
    mock_add_management_channel_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_remove_management_channel():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="admin",
            subcommand_name="remove-management-channel"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_route = AsyncMock(RemoveManagementChannelRoute, autospec=True)
    mock_route.call.return_value = mock_response

    # When
    router = _router(remove_management_channel_route=mock_route)
    response = await router.route(event)

    # Then
    mock_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_add_management_role():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="admin",
            subcommand_name="add-management-role"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_route = AsyncMock(AddManagementRoleRoute, autospec=True)
    mock_route.call.return_value = mock_response

    # When
    router = _router(add_management_role_route=mock_route)
    response = await router.route(event)

    # Then
    mock_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_admin_remove_management_role():
    # Given
    event = DiscordEvent(
        command=DiscordCommand(
            command_name="admin",
            subcommand_name="remove-management-role"
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.acknowledge()

    mock_route = AsyncMock(RemoveManagementRoleRoute, autospec=True)
    mock_route.call.return_value = mock_response

    # When
    router = _router(remove_management_role_route=mock_route)
    response = await router.route(event)

    # Then
    mock_route.call.assert_called_with(event)

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


def _router(
        ping_route=None,
        guess_route=None,
        create_route=None,
        post_route=None,
        close_game_route=None,
        list_games_route=None,
        guild_info_route=None,
        add_management_channel_route=None,
        remove_management_channel_route=None,
        add_management_role_route=None,
        remove_management_role_route=None,
):
    return RouterImpl(
        ping_route=ping_route or Route(),
        guess_route=guess_route or Route(),
        create_route=create_route or Route(),
        post_route=post_route or Route(),
        close_game_route=close_game_route or Route(),
        list_games_route=list_games_route or Route(),
        guild_info_route=guild_info_route or Route(),
        add_management_channel_route=add_management_channel_route or Route(),
        remove_management_channel_route=remove_management_channel_route or Route(),
        add_management_role_route=add_management_role_route or Route(),
        remove_management_role_route=remove_management_role_route or Route(),
    )
