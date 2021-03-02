import logging
from enum import Enum

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ResponseType(Enum):
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNEL_MESSAGE = 3
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    ACKNOWLEDGE_WITH_SOURCE = 5


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
        if self.response_type in [ResponseType.CHANNEL_MESSAGE, ResponseType.CHANNEL_MESSAGE_WITH_SOURCE]:
            return {
                'type': self.response_type.value,
                'data': {
                    'content': self.content,
                    'allowed_mentions': {
                        'parse': self.allowed_mention_types
                    }
                }
            }
        else:
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

    @classmethod
    def channel_message(cls, message: str):
        log.error("DO NOT USE! The timeout of 3 seconds is too short. Send a custom message instead.")
        assert False
        # return DiscordResponse(
        #     response_type=ResponseType.CHANNEL_MESSAGE,
        #     content=message
        # )

    @classmethod
    def channel_message_with_source(cls, message: str):
        log.error("DO NOT USE! The timeout of 3 seconds is too short. Send a custom message instead.")
        assert False
        # return DiscordResponse(
        #     response_type=ResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        #     content=message
        # )

    @classmethod
    def acknowledge_with_source(cls):
        return DiscordResponse(
            response_type=ResponseType.ACKNOWLEDGE_WITH_SOURCE
        )
