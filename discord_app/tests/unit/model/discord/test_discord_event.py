from eternal_guesses.model.discord import discord_event
from eternal_guesses.model.discord.discord_component import ComponentType


def test_from_ping_event():
    # Given
    event_body = {
        "id": "5002",
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82d",
        "type": 1,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.command.command_name == "ping"


def test_member_from_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "guess",
            "options": [
                {
                    "name": "game-id",
                    "value": "test"
                },
                {
                    "name": "guess",
                    "value": "1000"
                }
            ]
        },
        "guild_id": "4001",
        "id": "5001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": "User-Nickname",
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [
                "9999",
            ],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.member.username == "User-Name"
    assert event.member.nickname == "User-Nickname"
    assert event.member.user_id == 9001
    assert event.member.roles == [
        9999
    ]


def test_from_manage_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "eternal-guess",
            "options": [
                {
                    "name": "manage",
                    "options": [
                        {
                            "name": "post",
                            "options": [
                                {
                                    "name": "game-id",
                                    "value": "test-game"
                                },
                                {
                                    "name": "channel",
                                    "value": "3001"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "guild_id": "4001",
        "id": "5001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 4001

    command = event.command
    assert command.command_id == 2001
    assert command.command_name == "manage"
    assert command.subcommand_name == "post"
    assert command.options['game-id'] == 'test-game'
    assert command.options['channel'] == '3001'


def test_from_manage_list_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "eternal-guess",
            "options": [
                {
                    "name": "manage",
                    "options": [
                        {
                            "name": "list-games",
                            "options": [
                                {
                                    "name": "closed",
                                    "value": True
                                },
                            ]
                        }
                    ]
                }
            ]
        },
        "guild_id": "4001",
        "id": "5001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 4001

    command = event.command
    assert command.command_id == 2001
    assert command.command_name == "manage"
    assert command.subcommand_name == "list-games"
    assert command.options['closed']


def test_from_manage_list_without_options_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "eternal-guess",
            "options": [
                {
                    "name": "manage",
                    "options": [
                        {
                            "name": "list",
                        }
                    ]
                }
            ]
        },
        "guild_id": "4001",
        "id": "5001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 4001

    command = event.command
    assert command.command_id == 2001
    assert command.command_name == "manage"
    assert command.subcommand_name == "list"
    assert 'closed' not in command.options


def test_from_admin_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "eternal-guess",
            "options": [
                {
                    "name": "admin",
                    "options": [
                        {
                            "name": "add-management-role",
                            "options": [
                                {
                                    "name": "role",
                                    "value": "3001"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "guild_id": "4001",
        "id": "5001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 4001

    command = event.command
    assert command.command_id == 2001
    assert command.command_name == "admin"
    assert command.subcommand_name == "add-management-role"
    assert command.options == {
        "role": "3001"
    }


def test_from_guess_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "guess",
            "options": [
                {
                    "name": "game-id",
                    "value": "test"
                },
                {
                    "name": "guess",
                    "value": "1000"
                }
            ]
        },
        "guild_id": "4001",
        "id": "5001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 4001

    command = event.command
    assert command.command_id == 2001
    assert command.command_name == "guess"
    assert command.subcommand_name is None
    assert command.options == {
        "game-id": "test",
        "guess": "1000",
    }


def test_from_create_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "eternal-guess",
            "options": [
                {
                    "name": "create",
                    "options": [
                        {
                            "name": "game-id",
                            "value": "test-game-1"
                        }
                    ]
                }
            ]
        },
        "guild_id": "3001",
        "id": "4001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 3001

    command = event.command
    assert command.command_id == 2001
    assert command.command_name == "create"
    assert command.subcommand_name is None
    assert command.options == {
        "game-id": "test-game-1",
    }


def test_from_create_without_options_command_event():
    # Given
    event_body = {
        "channel_id": "1001",
        "data": {
            "id": "2001",
            "name": "eternal-guess",
            "options": [
                {
                    "name": "create",
                }
            ]
        },
        "guild_id": "3001",
        "id": "4001",
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": 2,
        "version": 1
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    command = event.command
    assert command.options == {}


# https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-modal
def test_from_modal_submit_event():
    event_body = {
        'type': 5,
        'version': 1,
        'channel_id': '1001',
        'data': {
            'components': [{
                'components': [{
                    'custom_id': 'test_input',
                    'type': 4,
                    'value': '500'
                }],
                'type': 1
            }],
            'custom_id': 'test_modal'
        },
        'guild_id': '2001',
        'id': '3001',
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        'token': 'whfjwhfukwynexfl823yflwf9wauf928fh82e',
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 2001

    modal_submit = event.modal_submit
    assert modal_submit.modal_custom_id == 'test_modal'
    assert modal_submit.inputs['test_input'] == '500'


def test_from_message_component_event():
    event_body = {
        'type': 3,
        'version': 1,
        'channel_id': '1001',
        'data': {
            'component_type': 2,
            'custom_id': 'test_button_primary'
        },
        'guild_id': '2001',
        'id': '3001',
        'message': {
            # Not used.
        },
        "member": {
            "deaf": False,
            "is_pending": False,
            "joined_at": "2021-01-16T20:21:19.053000+00:00",
            "mute": False,
            "nick": None,
            "pending": False,
            "permissions": "2147483647",
            "premium_since": None,
            "roles": [],
            "user": {
                "avatar": "abcdefghijklmop",
                "discriminator": "5",
                "id": "9001",
                "public_flags": 0,
                "username": "User-Name"
            }
        },
        'token': 'whfjwhfukwynexfl823yflwf9wauf928fh82e',
    }

    # When
    event = discord_event.from_event(event_body)

    # Then
    assert event.channel_id == 1001
    assert event.guild_id == 2001

    component_action = event.component_action
    assert component_action.component_custom_id == 'test_button_primary'
    assert component_action.component_type == ComponentType.BUTTON
