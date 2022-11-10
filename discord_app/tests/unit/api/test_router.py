import json
from unittest.mock import AsyncMock

import pytest

from eternal_guesses.api.route_definition import ComponentActionRouteDefinition, \
    ModalSubmitRouteDefinition
from eternal_guesses.api.route_handler import RouteHandler
from eternal_guesses.api.router import RouterImpl
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_component_action import \
    DiscordComponentAction
from eternal_guesses.model.discord.discord_event import DiscordEvent, \
    DiscordCommand
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.discord.discord_modal_submit import \
    DiscordModalSubmit
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route

pytestmark = pytest.mark.asyncio


async def test_handle_component_action():
    # Given
    event = DiscordEvent(
        component_action=DiscordComponentAction(
            component_type=ComponentType.BUTTON,
            component_custom_id="button_trigger_guess_modal_game_id"
        )
    )

    mock_response = DiscordResponse.ephemeral_channel_message("Component action well handled.")

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
    assert type(arguments[1]) == ComponentActionRouteDefinition
    assert arguments[1].component_type == ComponentType.BUTTON
    assert arguments[1].custom_id_starts_with == "button_trigger_guess_modal_"

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_modal_submit_action():
    # Given
    event = DiscordEvent(
        modal_submit=DiscordModalSubmit(
            modal_custom_id="modal_submit_guess_game_id",
            inputs={
                "modal_input_guess_value_game_id": "500"
            }
        )
    )

    mock_response = DiscordResponse.ephemeral_channel_message("Modal submission well handled.")

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
    assert type(arguments[1]) == ModalSubmitRouteDefinition
    assert arguments[1].custom_id_starts_with == "modal_submit_guess_"

    assert response.status_code == 200
    assert json.loads(response.body) == mock_response.json()


async def test_handle_command():
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
    edit_guess_route=None,
    delete_guess_route=None,
    submit_guess_route=None,
    trigger_guess_modal_route=None,
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
        edit_guess_route=edit_guess_route or Route(),
        delete_guess_route=delete_guess_route or Route(),
        modal_test_route=Route(),
        message_with_buttons_route=Route(),
        submit_guess_route=submit_guess_route or Route(),
        trigger_guess_modal_route=trigger_guess_modal_route or Route(),
        manage_game_route=Route(),
        action_post_game_route=Route(),
        action_trigger_delete_guess_route=Route(),
        action_trigger_edit_guess_route=Route(),
        submit_create_route=Route(),
    )
