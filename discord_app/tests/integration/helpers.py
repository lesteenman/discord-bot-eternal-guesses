import json
from typing import Dict, List

from eternal_guesses.model.discord_event import CommandType


def create_context() -> Dict:
    return {}


def create_admin_event(subcommand: str = None, options: List = None,
                       guild_id: int = 1000, channel_id: int = 2000) -> Dict:
    if options is None:
        options = []

    event_body = _base_event_body(guild_id, channel_id)

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


def _create_member() -> Dict:
    return {
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
    }


def _make_event(body: Dict) -> Dict:
    return {
        'body': json.dumps(body),
        'headers': {},
    }


def _base_event_body(guild_id, channel_id):
    return {
        "channel_id": channel_id,
        "guild_id": guild_id,
        "data": None,
        "id": "9991",
        "member": _create_member(),
        "token": "whfjwhfukwynexfl823yflwf9wauf928fh82e",
        "type": CommandType.COMMAND.value,
        "version": 1
    }
