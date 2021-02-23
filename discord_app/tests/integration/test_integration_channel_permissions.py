from eternal_guesses import handler
from tests.integration.helpers import create_context, make_discord_manage_list_event


def test_integration_channel_permissions():
    # Given
    guild_id = 1
    manage_channel = 100
    manage_role = 200

    # When we allow one channel and one role as management
    add_management_channel(guild_id=guild_id, manage_channel=manage_channel)
    add_management_role(guild_id=guild_id, manage_role=manage_role)

    # If we perform a management action as a different role or channel, it is disallowed
    new_channel = 101
    new_role = 201
    assert manage_list_games(guild_id=1, channel_id=101, role_id=201) == 401

    # And if we


def add_management_channel(guild_id, manage_channel):
    pass


def add_management_role(guild_id, manage_role):
    pass


def manage_list_games(guild_id, channel_id, role_id) -> int:
    response = handler.handle_lambda(
        make_discord_manage_list_event(guild_id=guild_id, channel_id=channel_id, role_id=role_id),
        create_context()
    )

    return response['statusCode']
