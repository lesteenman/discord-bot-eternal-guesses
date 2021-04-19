import json
from unittest.mock import AsyncMock

import pytest

from eternal_guesses.api.route_handler import RouteHandler
from eternal_guesses.api.router import RouterImpl
from eternal_guesses.model.discord.discord_event import DiscordEvent, DiscordCommand
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route

pytestmark = pytest.mark.asyncio


async def test_handle():
    # Given
    command_name = "admin"
    subcommand_name = "info"

    event = DiscordEvent(
        command=DiscordCommand(
            command_name=command_name,
            subcommand_name=subcommand_name,
        ),
        member=DiscordMember()
    )

    mock_response = DiscordResponse.ephemeral_channel_message("Well handled brother!")

    mock_route_handler = AsyncMock(RouteHandler)
    mock_route_handler.handle.return_value = mock_response

    router = _router(
        route_handler=mock_route_handler,
    )

    # When
    response = await router.route(event)

    # Then
    mock_route_handler.handle.assert_called()
    arguments = mock_route_handler.handle.call_args[0]
    assert arguments[0] == event
    assert arguments[1].command == command_name
    if subcommand_name:
        assert arguments[1].subcommand == subcommand_name

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


def _router(
        route_handler,
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
        route_handler=route_handler,
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
