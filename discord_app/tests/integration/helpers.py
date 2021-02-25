import json
from typing import Dict, List

from eternal_guesses.model.discord_event import CommandType

# DEFAULT_GUILD_ID = 100
# DEFAULT_GAME_ID = 200
DEFAULT_CHANNEL_ID = 300
DEFAULT_USER_ID = 400
DEFAULT_ROLE_ID = 500
DEFAULT_USER_NAME = "default-username"
DEFAULT_MEMBER_NICK = "default-nickname"


def create_context() -> Dict:
    return {}


def make_discord_guess_event(guild_id: int, game_id: str, guess: str, user_id: int = DEFAULT_USER_ID,
                             role_id: int = DEFAULT_ROLE_ID,
                             channel_id: int = DEFAULT_CHANNEL_ID, member_nickname: str = DEFAULT_MEMBER_NICK,
                             user_name: str = DEFAULT_USER_NAME):
    event_body = _base_event_body(guild_id=guild_id, channel_id=channel_id, user_id=user_id,
                                  member_nickname=member_nickname, user_name=user_name, role_id=role_id)
    event_body['data'] = {
        "id": "2001",
        "name": "guess",
        "options": [
            {
                "name": "game-id",
                "value": game_id
            },
            {
                "name": "guess",
                "value": guess
            }
        ]
    }

    return _make_event(event_body)


def make_discord_create_event(guild_id: int, game_id: str, channel_id: int = DEFAULT_CHANNEL_ID,
                              user_id: int = DEFAULT_USER_ID, member_nickname: str = DEFAULT_MEMBER_NICK,
                              user_name: str = DEFAULT_USER_NAME, role_id: int = DEFAULT_ROLE_ID):
    event_body = _base_event_body(guild_id=guild_id, channel_id=channel_id, user_id=user_id,
                                  member_nickname=member_nickname, user_name=user_name, role_id=role_id)
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "create",
                "options": [
                    {
                        "name": "game-id",
                        "value": game_id
                    }
                ]
            }
        ]
    }

    return _make_event(event_body)


def make_discord_admin_event(guild_id: int, subcommand: str = None, options: List = None,
                             role_id: int = DEFAULT_ROLE_ID,
                             channel_id: int = DEFAULT_CHANNEL_ID, user_id: int = DEFAULT_USER_ID,
                             member_nickname: str = DEFAULT_MEMBER_NICK,
                             user_name: str = DEFAULT_USER_NAME) -> Dict:
    if options is None:
        options = []

    event_body = _base_event_body(guild_id=guild_id, channel_id=channel_id, user_id=user_id,
                                  member_nickname=member_nickname, user_name=user_name, role_id=role_id)

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


def make_discord_manage_post_event(guild_id: int, game_id: str, channel_id: int, user_id: int = DEFAULT_USER_ID,
                                   role_id: int = DEFAULT_ROLE_ID,
                                   member_nickname: str = DEFAULT_MEMBER_NICK,
                                   user_name: str = DEFAULT_USER_NAME) -> Dict:
    event_body = _base_event_body(guild_id=guild_id, channel_id=channel_id, user_id=user_id,
                                  member_nickname=member_nickname, user_name=user_name, role_id=role_id)
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
                                "value": game_id
                            },
                            {
                                "name": "channel",
                                "value": channel_id
                            }
                        ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def make_discord_manage_list_event(guild_id: int, channel_id: int, user_id: int = DEFAULT_USER_ID,
                                   role_id: int = DEFAULT_ROLE_ID,
                                   member_nickname: str = DEFAULT_MEMBER_NICK,
                                   user_name: str = DEFAULT_USER_NAME) -> Dict:
    event_body = _base_event_body(guild_id=guild_id, channel_id=channel_id, user_id=user_id,
                                  member_nickname=member_nickname, user_name=user_name, role_id=role_id)
    event_body['data'] = {
        "id": "2001",
        "name": "eternal-guess",
        "options": [
            {
                "name": "manage",
                "options": [
                    {
                        "name": "list-games",
                        # "options": [
                        #     {
                        #         "name": "closed",
                        #         "value": False
                        #     },
                        # ]
                    }
                ]
            }
        ]

    }

    return _make_event(event_body)


def _create_member(user_id: int, member_nickname: str, user_name: str, role_id: int) -> Dict:
    return {
        "deaf": False,
        "is_pending": False,
        "joined_at": "2021-01-16T20:21:19.053000+00:00",
        "mute": False,
        "nick": member_nickname,
        "pending": False,
        "permissions": "2147483647",
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


def _base_event_body(guild_id, channel_id, user_id, member_nickname, user_name, role_id):
    return {
        "channel_id": channel_id,
        "guild_id": guild_id,
        "data": None,
        "id": "9991",
        "member": _create_member(
            user_id=user_id,
            member_nickname=member_nickname,
            user_name=user_name,
            role_id=role_id
        ),
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": CommandType.COMMAND.value,
        "version": 1
    }
