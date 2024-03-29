from typing import Dict

from loguru import logger


class DiscordCommand:
    def __init__(
        self,
        command_id: int = -1,
        command_name: str = None,
        subcommand_name: str = None,
        options: Dict = None
    ):
        self.command_id = int(command_id)
        self.command_name = command_name
        self.subcommand_name = subcommand_name

        if options is None:
            options = {}
        self.options = options

    def __repr__(self):
        return f"<DiscordCommand command_id={self.command_id} command_name={self.command_name} " \
               f"subcommand_name={self.subcommand_name} options={self.options}>"


def _command_from_data(event_data):
    if event_data['name'] == "eternal-guess":
        if event_data['options'][0]['name'] == "create":
            return _create_command_from_data(event_data)

        if event_data['options'][0]['name'] == "admin":
            return _admin_or_manage_command_from_data(event_data)

        if event_data['options'][0]['name'] == "manage":
            return _admin_or_manage_command_from_data(event_data)

        raise UnknownCommandError(event_data)

    try:
        return _test_command_from_data(event_data)
    except Exception as e:
        logger.exception(e)
        raise UnknownCommandError(event_data)


def _guess_command_from_data(event_data: Dict) -> DiscordCommand:
    options = {}
    for option in event_data['options']:
        options[option['name']] = option['value']

    return DiscordCommand(
        command_id=event_data['id'],
        command_name=event_data['name'], options=options
    )


def _test_command_from_data(event_data: Dict) -> DiscordCommand:
    options = None
    if 'options' in event_data:
        options = {}
        for o in event_data['options']:
            options[o['name']] = o['value']

    return DiscordCommand(
        command_id=event_data['id'],
        command_name=event_data['name'],
        options=options
    )


def _create_command_from_data(event_data: Dict) -> DiscordCommand:
    command_id = event_data['id']

    sub_command = event_data['options'][0]
    command_name = sub_command['name']

    options = {}
    for option in sub_command.get('options', {}):
        options[option['name']] = option['value']

    return DiscordCommand(
        command_id=command_id, command_name=command_name,
        options=options
    )


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


class UnknownCommandError(Exception):
    def __init__(self, event_data):
        super().__init__(f"Could not handle unknown command:\n{event_data}")
