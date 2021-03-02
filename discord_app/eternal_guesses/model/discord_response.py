from enum import Enum


class ResponseType(Enum):
    PONG = 1
    ACKNOWLEDGE = 2
    # ACKNOWLEDGE_WITH_SOURCE = 5


class DiscordResponse(object):
    def __init__(self, response_type: ResponseType, content: str = None, allow_role_mentions: bool = False,
                 allow_user_mentions: bool = False):
        self.response_type = response_type
        self.content = content

        self.allowed_mention_types = []
        if allow_user_mentions:
            self.allowed_mention_types.append('users')
        if allow_role_mentions:
            self.allowed_mention_types.append('roles')

    def json(self):
        return {
            'type': self.response_type.value
        }

    @classmethod
    def pong(cls):
        return DiscordResponse(
            response_type=ResponseType.PONG
        )

    @classmethod
    def acknowledge(cls):
        return DiscordResponse(
            response_type=ResponseType.ACKNOWLEDGE
        )

    # @classmethod
    # def acknowledge_with_source(cls):
    #     return DiscordResponse(
    #         response_type=ResponseType.ACKNOWLEDGE_WITH_SOURCE
    #     )
