from eternal_guesses import handler
from eternal_guesses.model.data.guild_config import GuildConfig
from tests.integration.helpers import create_context, make_discord_manage_list_event


def test_integration_channel_permissions():
    # Given
    guild_id = 1
    management_channel = 100
    management_role = 200

    # When we allow one channel and one role as management
    add_management_channel(guild_id=guild_id, manage_channel=management_channel)
    add_management_role(guild_id=guild_id, manage_role=management_role)

    # We see it in the config
    config = get_guild_config(guild_id=guild_id)
    assert management_channel in config.management_channels
    assert management_role in config.management_roles

    # If we perform a management action as a different role or channel, it is disallowed
    other_channel = 101
    other_role = 201
    assert manage_list_games(guild_id=1, channel_id=other_channel, role_id=other_role) == 401

    # But if we do it from the correct channel, it is allowed


def add_management_channel(guild_id, manage_channel):
    assert False # Implement a call to admin.add-channel


def add_management_role(guild_id, manage_role):
    assert False # Implement a call to admin.add-role


def get_guild_config(guild_id) -> GuildConfig:
    assert False # get from the repository


def manage_list_games(guild_id, channel_id, role_id) -> int:
    response = handler.handle_lambda(
        make_discord_manage_list_event(guild_id=guild_id, channel_id=channel_id, role_id=role_id),
        create_context()
    )

    return response['statusCode']
