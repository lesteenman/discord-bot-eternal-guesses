import json
import typing

from eternal_guesses import event_handler
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.repositories.configs_repository import \
    ConfigsRepositoryImpl
from tests.integration.helpers import make_discord_manage_list_event, \
    make_discord_admin_add_channel_event, make_discord_admin_add_role_event, \
    make_discord_admin_info, \
    make_discord_admin_remove_channel_event, \
    make_discord_admin_remove_role_event


def test_integration_channel_permissions(eternal_guesses_table):
    # Given
    guild_id = 1
    management_channel = 100
    management_role = 200

    # When we allow one channel and one role as management
    add_management_channel(guild_id=guild_id, channel_id=management_channel)
    add_management_role(guild_id=guild_id, management_role=management_role)

    # We see it in the config
    config = get_guild_config(eternal_guesses_table=eternal_guesses_table, guild_id=guild_id)
    assert management_channel in config.management_channels
    assert management_role in config.management_roles

    # If we perform a management action as a different role or channel, it is disallowed
    other_channel = 101
    other_role = 201
    response = manage_list_games(guild_id=1, channel_id=other_channel, role_id=other_role)
    assert is_disallowed_message(response)

    # But if we do it from the correct channel, it is allowed
    response = manage_list_games(guild_id=1, channel_id=management_channel, role_id=other_role)
    assert not is_disallowed_message(response)

    # And doing it with the correct role is also allowed
    response = manage_list_games(guild_id=1, channel_id=other_channel, role_id=management_role)
    assert not is_disallowed_message(response)

    # If we delete the channel again, it's no longer allowed
    remove_management_channel(guild_id=guild_id, management_channel_id=management_channel)
    response = manage_list_games(guild_id=1, channel_id=management_channel, role_id=other_role)
    assert is_disallowed_message(response)

    # If we delete the role again, that too is no longer allowed
    remove_management_role(guild_id=guild_id, management_role=management_role)
    response = manage_list_games(guild_id=1, channel_id=management_channel, role_id=management_role)
    assert is_disallowed_message(response)

    # Getting the admin info only works when done as an Admin
    response = admin_info(guild_id=guild_id, channel_id=management_channel, role_id=management_role, is_admin=False)
    assert is_disallowed_message(response)

    response = admin_info(guild_id=guild_id, channel_id=other_channel, role_id=other_role, is_admin=True)
    assert not is_disallowed_message(response)


def add_management_channel(guild_id, channel_id):
    response = event_handler.handle(
        make_discord_admin_add_channel_event(guild_id=guild_id, new_management_channel_id=channel_id, is_admin=True),
    )

    assert response['statusCode'] == 200
    return json.loads(response['body'])


def remove_management_channel(guild_id, management_channel_id: int):
    response = event_handler.handle(
        make_discord_admin_remove_channel_event(guild_id=guild_id, management_channel_id=management_channel_id,
                                                is_admin=True),
    )

    assert response['statusCode'] == 200
    return json.loads(response['body'])


def admin_info(guild_id: int, channel_id: int, role_id: int, is_admin: bool):
    response = event_handler.handle(
        make_discord_admin_info(guild_id=guild_id, channel_id=channel_id, role_id=role_id, is_admin=is_admin),
    )

    assert response['statusCode'] == 200
    return json.loads(response['body'])


def add_management_role(guild_id, management_role):
    response = event_handler.handle(
        make_discord_admin_add_role_event(guild_id=guild_id, new_management_role=management_role, is_admin=True),
    )

    assert response['statusCode'] == 200
    return json.loads(response['body'])


def remove_management_role(guild_id, management_role):
    response = event_handler.handle(
        make_discord_admin_remove_role_event(guild_id=guild_id, management_role=management_role, is_admin=True),
    )

    assert response['statusCode'] == 200
    return json.loads(response['body'])


def get_guild_config(eternal_guesses_table, guild_id) -> GuildConfig:
    configs_repository = ConfigsRepositoryImpl(eternal_guesses_table)
    return configs_repository.get(guild_id=guild_id)


def manage_list_games(guild_id, channel_id, role_id) -> dict:
    response = event_handler.handle(
        make_discord_manage_list_event(guild_id=guild_id, channel_id=channel_id, role_id=role_id),
    )

    assert response['statusCode'] == 200
    return json.loads(response['body'])


def is_disallowed_message(response: typing.Dict):
    return 'data' in response and response['data']['flags'] & 64 == 64 \
           and "You are not allowed" in response['data']['content']
