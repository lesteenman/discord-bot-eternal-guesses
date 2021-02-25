from enum import Enum
from typing import Dict

from discord_interactions import InteractionType

from eternal_guesses.model.discord_member import DiscordMember, _member_from_data


class UnknownCommandError(Exception):
    def __init__(self, event_data):
        super(f"Could not handle unknown command:\n{event_data}")


class CommandType(Enum):
    PING = 1
    COMMAND = 2


class DiscordCommand:
    def __init__(self, command_id: str, command_name: str, subcommand_name: str = None, options: Dict = None):
        self.command_id = command_id
        self.command_name = command_name
        self.subcommand_name = subcommand_name

        if options is None:
            options = {}
        self.options = options


class DiscordEvent:
    def __init__(self, command_type: CommandType, command: DiscordCommand = None, member: DiscordMember = None,
                 guild_id: int = None, channel_id: int = None):
        self.type = command_type
        self.command = command
        self.member = member
        self.guild_id = guild_id
        self.channel_id = channel_id


def _guess_command_from_data(event_data: Dict) -> DiscordCommand:
    options = {}
    for option in event_data['options']:
        options[option['name']] = option['value']

    return DiscordCommand(command_id=event_data['id'], command_name=event_data['name'], options=options)


def _create_command_from_data(event_data: Dict) -> DiscordCommand:
    command_id = event_data['id']

    sub_command = event_data['options'][0]
    command_name = sub_command['name']

    options = {}
    for option in sub_command.get('options', {}):
        options[option['name']] = option['value']

    return DiscordCommand(command_id=command_id, command_name=command_name, options=options)


def _admin_or_manage_command_from_data(event_data: Dict) -> DiscordCommand:
    command_id = event_data['id']
    command_name = event_data['options'][0]['name']

    sub_command = event_data['options'][0]['options'][0]
    subcommand_name = sub_command['name']

    options = {}
    for option in sub_command.get('options', {}):
        options[option['name']] = option['value']

    return DiscordCommand(
        command_id=command_id,
        command_name=command_name,
        subcommand_name=subcommand_name,
        options=options
    )


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


def from_event(event_source: Dict) -> DiscordEvent:
    if event_source['type'] == InteractionType.PING:
        return DiscordEvent(command_type=CommandType.PING)
    else:
        return DiscordEvent(
            command_type=CommandType.COMMAND,
            channel_id=event_source['channel_id'],
            guild_id=event_source['guild_id'],
            command=_command_from_data(event_source['data']),
            member=_member_from_data(event_source['member'])
        )
