import json
from typing import Dict, List

from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_event import InteractionType

# DEFAULT_GUILD_ID = 100
# DEFAULT_GAME_ID = 200
DEFAULT_CHANNEL_ID = 300
DEFAULT_USER_ID = 400
DEFAULT_ROLE_ID = 500
DEFAULT_USER_NAME = "default-username"
DEFAULT_MEMBER_NICK = "default-nickname"


def component_action(
    guild_id: int,
    component_custom_id: str,
    component_type: ComponentType,
    user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    channel_id: int = DEFAULT_CHANNEL_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
):
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False,
        event_type=InteractionType.MESSAGE_COMPONENT,
    )
    event_body['data'] = {
        "custom_id": component_custom_id,
        "component_type": component_type.value,
    }

    return _make_event(event_body)


def modal_submit_event(
    guild_id: int,
    modal_custom_id: str,
    inputs: dict[str, str],
    user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    channel_id: int = DEFAULT_CHANNEL_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
):
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False,
        event_type=InteractionType.MODAL_SUBMIT,
    )
    event_body['data'] = {
        "custom_id": modal_custom_id,
        "components": [
            {
                'type': ComponentType.ACTION_ROW.value,
                'components': [
                    {
                        "type": ComponentType.TEXT_INPUT.value,
                        "custom_id": k,
                        "value": v,
                    }
                ]
            } for k, v in inputs.items()
        ],
    }

    return _make_event(event_body)


def application_command(
    command_name: str,
    guild_id: int,
    channel_id: int = DEFAULT_CHANNEL_ID,
    user_id: int = DEFAULT_USER_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME,
    role_id: int = DEFAULT_ROLE_ID,
):
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )

    event_body['data'] = {
        "id": "2001",
        "name": command_name,
    }

    return _make_event(event_body)


def make_discord_create_event(
    guild_id: int,
    channel_id: int = DEFAULT_CHANNEL_ID,
    user_id: int = DEFAULT_USER_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME,
    role_id: int = DEFAULT_ROLE_ID,
):
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )

    event_body['data'] = {
        "id": "2001",
        "name": "create-game",
    }

    return _make_event(event_body)


def make_discord_admin_event(
    guild_id: int, subcommand: str = None, options: List = None,
    role_id: int = DEFAULT_ROLE_ID,
    channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    if options is None:
        options = []

    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )

    event_body['data'] = {
        "id": "1234",
        "name": "eternal-guess",
        "options": [
            {
                "name": "admin",
                "options": [
                    {
                        "name": subcommand,
                        "options": options,
                    }
                ]
            }
        ]
    }

    return _make_event(event_body)


def make_discord_manage_post_event(
    guild_id: int,
    game_id: str,
    channel_id: int,
    user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )
    event_body['data'] = {
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
                                "value": str(game_id)
                            },
                            {
                                "name": "channel",
                                "value": str(channel_id)
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_admin_add_channel_event(
    guild_id: int, new_management_channel_id: int, is_admin: bool,
    channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id, channel_id=channel_id, user_id=user_id,
        member_nickname=member_nickname, user_name=user_name, role_id=role_id,
        is_admin=is_admin
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "admin",
                "options": [
                    {
                        "name": "add-management-channel",
                        "options": [
                            {
                                "name": "channel",
                                "value": str(new_management_channel_id)
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_admin_remove_channel_event(
    guild_id: int, management_channel_id: int, is_admin: bool,
    channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id, channel_id=channel_id, user_id=user_id,
        member_nickname=member_nickname, user_name=user_name, role_id=role_id,
        is_admin=is_admin
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "admin",
                "options": [
                    {
                        "name": "remove-management-channel",
                        "options": [
                            {
                                "name": "channel",
                                "value": str(management_channel_id)
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_admin_add_role_event(
    guild_id: int, new_management_role: int, is_admin: bool,
    channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id, channel_id=channel_id, user_id=user_id,
        member_nickname=member_nickname, user_name=user_name, role_id=role_id,
        is_admin=is_admin
    )
    event_body['data'] = {
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
                                "value": str(new_management_role)
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_admin_remove_role_event(
    guild_id: int, management_role: int, is_admin: bool,
    channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id, channel_id=channel_id, user_id=user_id,
        member_nickname=member_nickname, user_name=user_name, role_id=role_id,
        is_admin=is_admin
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "admin",
                "options": [
                    {
                        "name": "remove-management-role",
                        "options": [
                            {
                                "name": "role",
                                "value": str(management_role)
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_admin_info(
    guild_id: int, is_admin: bool,
    channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id, channel_id=channel_id, user_id=user_id,
        member_nickname=member_nickname, user_name=user_name, role_id=role_id,
        is_admin=is_admin
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "admin",
                "options": [
                    {
                        "name": "info",
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_manage_list_event(
    guild_id: int, channel_id: int, user_id: int = DEFAULT_USER_ID,
    role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "manage",
                "options": [
                    {
                        "name": "list-games",
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_change_guess_event(
    guild_id: int, game_id: str, new_guess: str, member: int, channel_id: int,
    user_id: int = DEFAULT_USER_ID, role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "manage",
                "options": [
                    {
                        "name": "edit-guess",
                        "options": [
                            {
                                "name": "game-id",
                                "value": str(game_id)
                            },
                            {
                                "name": "member",
                                "value": str(member)
                            },
                            {
                                "name": "guess",
                                "value": str(new_guess)
                            },
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_delete_guess_event(
    guild_id: int, game_id: str, member: int, channel_id: int,
    user_id: int = DEFAULT_USER_ID, role_id: int = DEFAULT_ROLE_ID,
    member_nickname: str = DEFAULT_MEMBER_NICK,
    user_name: str = DEFAULT_USER_NAME
) -> Dict:
    event_body = _base_event_body(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        member_nickname=member_nickname,
        user_name=user_name,
        role_id=role_id,
        is_admin=False
    )
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "manage",
                "options": [
                    {
                        "name": "delete-guess",
                        "options": [
                            {
                                "name": "game-id",
                                "value": str(game_id)
                            },
                            {
                                "name": "member",
                                "value": str(member)
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def _create_member(
    user_id: int,
    member_nickname: str,
    user_name: str,
    role_id: int,
    is_admin: bool
) -> Dict:
    permissions = 0
    if is_admin:
        permissions = permissions | 0x8

    return {
        "deaf": False,
        "is_pending": False,
        "joined_at": "2021-01-16T20:21:19.053000+00:00",
        "mute": False,
        "nick": member_nickname,
        "pending": False,
        "permissions": permissions,
        "premium_since": None,
        "roles": [
            role_id,
        ],
        "user": {
            "avatar": "abcdefghijklmop",
            "discriminator": "5",
            "id": user_id,
            "public_flags": 0,
            "username": user_name
        }
    }


def _make_event(body: Dict) -> Dict:
    return {
        'body': json.dumps(body),
        'headers': {},
    }


def _base_event_body(
    guild_id: int,
    channel_id: int,
    user_id: int,
    member_nickname: str,
    user_name: str,
    role_id: int,
    is_admin: bool,
    event_type: InteractionType = InteractionType.APPLICATION_COMMAND
):
    return {
        "channel_id": channel_id,
        "guild_id": guild_id,
        "data": None,
        "id": "9991",
        "member": _create_member(
            user_id=user_id,
            member_nickname=member_nickname,
            user_name=user_name,
            role_id=role_id,
            is_admin=is_admin
        ),
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": event_type.value,
        "version": 1
    }
