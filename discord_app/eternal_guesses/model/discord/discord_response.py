from enum import Enum


class ResponseType(Enum):
    PONG = 1
    # ACKNOWLEDGE = 2  # TODO: Deprecated!
    CHANNEL_MESSAGE = 4
    DEFERRED_CHANNEL_MESSAGE = 5


class DiscordResponse(object):
    def __init__(self, response_type: ResponseType, content: str = None, allow_role_mentions: bool = False,
                 allow_user_mentions: bool = False):
        self.response_type = response_type
        self.content = content
        self.flags = 0

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
        else:
            data = {
                'flags': self.flags,
                'allowed_mentions': {
                    'parse': [],
                }
            }

            if self.content:
                data['content'] = self.content

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

    @property
    def is_ephemeral(self):
        return self.flags & 64 == 64

    @is_ephemeral.setter
    def is_ephemeral(self, value):
        if value:
            self.flags = self.flags | 64
        else:
            self.flags = self.flags & ~64
