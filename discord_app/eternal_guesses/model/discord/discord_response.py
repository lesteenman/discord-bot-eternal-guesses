from enum import Enum
from typing import List

import discord

from eternal_guesses.model.discord.discord_component import DiscordComponent, \
    ActionRow


class ResponseType(Enum):
    PONG = 1
    # ACKNOWLEDGE = 2  # TODO: Deprecated!
    CHANNEL_MESSAGE = 4
    DEFERRED_CHANNEL_MESSAGE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class DiscordResponse(object):
    def __init__(
        self,
        response_type: ResponseType,
        content: str = None,
        allow_role_mentions: bool = False,
        allow_user_mentions: bool = False,
        custom_id: str = None,
        title: str = None,
        action_rows: List[ActionRow] = None,
        embed: discord.Embed = None,
    ):
        self.response_type = response_type
        self.content = content
        self.flags = 0
        self.custom_id = custom_id
        self.title = title
        self.action_rows = action_rows
        self.embed = embed

        self.allowed_mention_types = []
        if allow_user_mentions:
            self.allowed_mention_types.append('users')
        if allow_role_mentions:
            self.allowed_mention_types.append('roles')

    def json(self):
        if self.response_type == ResponseType.PONG:
            return {
                'type': self.response_type.value
            }
        elif self.response_type == ResponseType.MODAL:
            data = {
                'custom_id': self.custom_id,
                'title': self.title,
                'components': [c.json() for c in self.action_rows],
            }

            return {
                'type': self.response_type.value,
                'data': data,
            }
        else:
            data = {
                'flags': self.flags,
                'allowed_mentions': {
                    'parse': [],
                }
            }

            if self.content:
                data['content'] = self.content

            if self.embed:
                data['embeds'] = [self.embed.to_dict()]

            if self.action_rows:
                data['components'] = [c.json() for c in self.action_rows]

            return {
                'type': self.response_type.value,
                'data': data,
            }

    @classmethod
    def pong(cls):
        return DiscordResponse(
            response_type=ResponseType.PONG
        )

    @classmethod
    def channel_message(cls):
        return DiscordResponse(
            response_type=ResponseType.CHANNEL_MESSAGE
        )

    @classmethod
    def ephemeral_channel_message(cls, content: str):
        response = DiscordResponse(
            response_type=ResponseType.CHANNEL_MESSAGE,
            content=content,
        )
        response.is_ephemeral = True

        return response

    @classmethod
    def deferred_channel_message(cls):
        return DiscordResponse(
            response_type=ResponseType.DEFERRED_CHANNEL_MESSAGE
        )

    @classmethod
    def modal(cls, custom_id: str, title: str, components: List[DiscordComponent]):
        return DiscordResponse(
            response_type=ResponseType.MODAL,
            custom_id=custom_id,
            title=title,
            action_rows=[ActionRow(
                components=[c],
            ) for c in components],
        )

    @property
    def is_ephemeral(self):
        return self.flags & 64 == 64

    @is_ephemeral.setter
    def is_ephemeral(self, value):
        if value:
            self.flags = self.flags | 64
        else:
            self.flags = self.flags & ~64
