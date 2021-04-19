from enum import Enum
from typing import Dict

from discord_interactions import InteractionType

from eternal_guesses.model.discord.discord_command import _command_from_data, DiscordCommand
from eternal_guesses.model.discord.discord_member import _member_from_data, DiscordMember


class CommandType(Enum):
    PING = 1
    COMMAND = 2


class DiscordEvent:
    def __init__(self,
                 command: DiscordCommand = None,
                 member: DiscordMember = None,
                 guild_id: int = None,
                 channel_id: int = None):
        self.command = command
        self.member = member
        self.guild_id = guild_id
        self.channel_id = channel_id


def from_event(event_source: Dict) -> DiscordEvent:
    if event_source['type'] == InteractionType.PING:
        return DiscordEvent(
            command=DiscordCommand(command_name="ping"),
        )
    else:
        channel_id = int(event_source['channel_id'])
        guild_id = int(event_source['guild_id'])
        command = _command_from_data(event_source['data'])
        member = _member_from_data(event_source['member'])

        return DiscordEvent(
            channel_id=channel_id,
            guild_id=guild_id,
            command=command,
            member=member
        )
