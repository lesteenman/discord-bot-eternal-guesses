from enum import Enum
from typing import Dict, List

from discord_interactions import InteractionType


class UnknownCommandError(Exception):
    def __init__(self, event_data):
        super(f"Could not handle unknown command:\n{event_data}")


class CommandType(Enum):
    PING = 1
    COMMAND = 2


class DiscordMember:
    username: str
    user_id: str
    roles: List[str]


class DiscordCommand:
    command_id: str
    command_name: str
    subcommand_name: str = None
    options: Dict = {}


class DiscordEvent:
    type: CommandType
    command: DiscordCommand = None
    member: DiscordMember = None
    guild_id: str = None
    channel_id: str = None


def _guess_command_from_data(event_data: Dict) -> DiscordCommand:
    command = DiscordCommand()

    command.command_id = event_data['id']
    command.command_name = event_data['name']

    command.options = {}
    for option in event_data['options']:
        command.options[option['name']] = option['value']

    return command


def _create_command_from_data(event_data: Dict) -> DiscordCommand:
    command = DiscordCommand()

    command.command_id = event_data['id']

    sub_command = event_data['options'][0]
    command.command_name = sub_command['name']

    command.options = {}
    for option in sub_command.get('options', {}):
        command.options[option['name']] = option['value']

    return command


def _admin_or_manage_command_from_data(event_data: Dict) -> DiscordCommand:
    command = DiscordCommand()

    command.command_id = event_data['id']
    command.command_name = event_data['options'][0]['name']

    sub_command = event_data['options'][0]['options'][0]
    command.subcommand_name = sub_command['name']

    command.options = {}
    for option in sub_command['options']:
        command.options[option['name']] = option['value']

    return command


def _command_from_data(event_data):
    if event_data['name'] == "guess":
        return _guess_command_from_data(event_data)

    if event_data['name'] == "eternal-guess":
        if event_data['options'][0]['name'] == "create":
            return _create_command_from_data(event_data)

        if event_data['options'][0]['name'] == "admin":
            return _admin_or_manage_command_from_data(event_data)

        if event_data['options'][0]['name'] == "manage":
            return _admin_or_manage_command_from_data(event_data)

    raise UnknownCommandError(event_data)


def _member_from_data(member_data: Dict) -> DiscordMember:
    member = DiscordMember()

    member.username = member_data['user']['username']
    member.user_id = member_data['user']['id']
    member.roles = member_data['roles']

    return member


def from_event(event_source: Dict) -> DiscordEvent:
    event = DiscordEvent()

    if event_source['type'] == InteractionType.PING:
        event.type = CommandType.PING
    else:
        event.type = CommandType.COMMAND
        event.channel_id = event_source['channel_id']
        event.guild_id = event_source['guild_id']
        event.command = _command_from_data(event_source['data'])
        event.member = _member_from_data(event_source['member'])

    return event
