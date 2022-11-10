from enum import Enum
from typing import Dict

from loguru import logger

from eternal_guesses.model.discord.discord_command import _command_from_data, \
    DiscordCommand
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_component_action import \
    DiscordComponentAction
from eternal_guesses.model.discord.discord_member import _member_from_data, \
    DiscordMember
from eternal_guesses.model.discord.discord_modal_submit import \
    DiscordModalSubmit


class InteractionType(Enum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class DiscordEvent:
    def __init__(
        self,
        command: DiscordCommand = None,
        modal_submit: DiscordModalSubmit = None,
        component_action: DiscordComponentAction = None,
        member: DiscordMember = None,
        guild_id: int = None,
        channel_id: int = None,
        event_type: InteractionType = InteractionType.APPLICATION_COMMAND,
    ):
        self.command = command
        self.modal_submit = modal_submit
        self.component_action = component_action
        self.member = member
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.event_type = event_type

    def __repr__(self):
        if self.event_type == InteractionType.APPLICATION_COMMAND:
            return f"<DiscordEvent command={self.command} member={self.member} guild_id={self.guild_id} " \
                   f"channel_id={self.channel_id} type={self.event_type}>"

        if self.event_type == InteractionType.MODAL_SUBMIT:
            return f"<DiscordEvent modal_submit={self.modal_submit} member={self.member} guild_id={self.guild_id} " \
                   f"channel_id={self.channel_id} type={self.event_type}>"

        if self.event_type == InteractionType.MESSAGE_COMPONENT:
            return f"<DiscordEvent message_component={self.component_action} member={self.member} guild_id={self.guild_id} " \
                   f"channel_id={self.channel_id} type={self.event_type}>"


def from_event(event_source: Dict) -> DiscordEvent:
    event_type = event_source['type']

    if event_type == InteractionType.PING.value:
        return from_ping_event()
    elif event_type == InteractionType.MESSAGE_COMPONENT.value:
        return from_message_component_event(event_source)
    elif event_type == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE.value:
        from_application_command_autocomplete_event(event_source)
    elif event_type == InteractionType.MODAL_SUBMIT.value:
        return from_modal_submit_event(event_source)
    elif event_type == InteractionType.APPLICATION_COMMAND.value:
        return from_application_command_event(event_source)


def from_application_command_event(event_source):
    channel_id = int(event_source['channel_id'])
    guild_id = int(event_source['guild_id'])
    command = _command_from_data(event_source['data'])
    member = _member_from_data(event_source['member'])
    return DiscordEvent(
        channel_id=channel_id,
        guild_id=guild_id,
        command=command,
        member=member,
        event_type=InteractionType.APPLICATION_COMMAND,
    )


def from_ping_event():
    return DiscordEvent(
        command=DiscordCommand(command_name="ping"),
    )


def from_message_component_event(event_source):
    channel_id = int(event_source['channel_id'])
    guild_id = int(event_source['guild_id'])
    member = _member_from_data(event_source['member'])

    component_type = ComponentType.from_value(
        event_source['data']['component_type']
    )

    if component_type == ComponentType.BUTTON:
        component_action = DiscordComponentAction(
            component_custom_id=event_source['data']['custom_id'],
            component_type=ComponentType.BUTTON,
        )
    elif component_type == ComponentType.STRING_SELECT:
        component_action = DiscordComponentAction(
            component_custom_id=event_source['data']['custom_id'],
            component_type=ComponentType.BUTTON,
            values=event_source['data']['values'],
        )
    else:
        raise NotImplementedError(f"Not implemented: component interaction of type {component_type}")

    return DiscordEvent(
        guild_id=guild_id,
        member=member,
        channel_id=channel_id,
        event_type=InteractionType.MESSAGE_COMPONENT,
        component_action=component_action,
    )


def from_application_command_autocomplete_event(event_source):
    logger.warning(
        f"Not implemented yet: handling app command autocomplete {event_source}"
    )
    raise NotImplementedError()


def from_modal_submit_event(event_source):
    channel_id = int(event_source['channel_id'])
    guild_id = int(event_source['guild_id'])
    member = _member_from_data(event_source['member'])

    custom_id = event_source['data']['custom_id']
    action_rows = event_source['data']['components']

    inputs = {}
    for row in action_rows:
        component = row['components'][0]
        inputs[component['custom_id']] = component['value']

    return DiscordEvent(
        channel_id=channel_id,
        guild_id=guild_id,
        member=member,
        event_type=InteractionType.MODAL_SUBMIT,
        modal_submit=DiscordModalSubmit(
            modal_custom_id=custom_id,
            inputs=inputs,
        )
    )
