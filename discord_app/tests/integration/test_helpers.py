import json

from eternal_guesses import event_handler
from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_response import ResponseType
from tests.integration import discord_events


def send_command(command_name, guild_id, options=None):
    options_dict = None
    if options:
        options_dict = [{"name": k, "value": v} for k, v in options.items()]

    response = event_handler.handle(
        discord_events.application_command(
            guild_id=guild_id,
            command_name=command_name,
            options=options_dict,
        )
    )
    assert response['statusCode'] == 200
    return response


def select_string(guild_id, component_custom_id, values):
    response = event_handler.handle(
        discord_events.component_action(
            guild_id=guild_id,
            component_custom_id=component_custom_id,
            component_type=ComponentType.STRING_SELECT,
            values=values,
        )
    )
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def select_channel(guild_id, component_custom_id, values):
    response = event_handler.handle(
        discord_events.component_action(
            guild_id=guild_id,
            component_custom_id=component_custom_id,
            component_type=ComponentType.CHANNEL_SELECT,
            values=values,
        )
    )
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def click_button_component(
    component_custom_id,
    guild_id,
    user_id=discord_events.DEFAULT_USER_ID
):
    event = discord_events.component_action(
        guild_id=guild_id,
        component_custom_id=component_custom_id,
        component_type=ComponentType.BUTTON,
        user_id=user_id,
    )
    response = event_handler.handle(event)
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def submit_modal(
    guild_id,
    modal_id,
    inputs,
    user_id=discord_events.DEFAULT_USER_ID
):
    response = event_handler.handle(
        discord_events.modal_submit_event(
            guild_id=guild_id,
            user_id=user_id,
            modal_custom_id=modal_id,
            inputs=inputs,
        ),
    )
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def is_modal_with_id(body, modal_id):
    if body['type'] != ResponseType.MODAL.value:
        return False

    return body['data']['custom_id'] == modal_id


def is_ephemeral_channel_message(body):
    # https://discord.com/developers/docs/resources/channel#message-object-message-flags
    return (
        body['type'] == ResponseType.CHANNEL_MESSAGE.value and
        body['data']['flags'] & (1 << 6)
    )


def has_input(body, component_custom_id):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.TEXT_INPUT.value and
                component['custom_id'] == component_custom_id
            ):
                return True

    return False


def has_selector_with_option(body, component_custom_id, value):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.STRING_SELECT.value and
                component['custom_id'] == component_custom_id and
                any([value == o['value'] for o in component['options']])
            ):
                return True

    return False


def has_channel_selector(body: dict, component_custom_id: str):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.CHANNEL_SELECT.value and
                component['custom_id'] == component_custom_id
            ):
                return True

    return False


def response_has_button(body, component_custom_id):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.BUTTON.value and
                component['custom_id'] == component_custom_id
            ):
                return True

    assert False


def trigger_manage_game_post(game_id: str, guild_id: int, is_closed: bool):
    # List the games
    if is_closed:
        response = send_command(
            command_name="list-games",
            guild_id=guild_id,
            options={"include-closed": True}
        )
    else:
        response = send_command(
            command_name="list-games",
            guild_id=guild_id
        )
    body = json.loads(response['body'])
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value

    # Verify the game is one of the options
    assert has_selector_with_option(
        body=body,
        component_custom_id=ComponentIds.component_select_game_to_manage,
        value=game_id
    )

    # Select the game to manage
    body = select_string(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_select_game_to_manage,
        values=[game_id],
    )
    return body
