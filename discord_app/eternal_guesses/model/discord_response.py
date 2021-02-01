from enum import Enum


class ResponseType(Enum):
    PONG = 1
    ACKNOWLEDGE = 2
    CHANNEL_MESSAGE = 3
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    ACKNOWLEDGE_WITH_SOURCE = 5


class DiscordResponse(object):
    type: ResponseType
    content: str = None

    def json(self):
        if self.type is ResponseType.CHANNEL_MESSAGE or self.type is ResponseType.CHANNEL_MESSAGE_WITH_SOURCE:
            return {
                'type': self.type.value,
                'data': {
                    'content': self.content
                }
            }
        else:
            return {
                'type': self.type.value
            }

    @classmethod
    def pong(cls):
        discord_response = DiscordResponse()
        discord_response.type = ResponseType.PONG
        return discord_response

    @classmethod
    def acknowledge(cls):
        discord_response = DiscordResponse()
        discord_response.type = ResponseType.ACKNOWLEDGE
        return discord_response

    @classmethod
    def channel_message(cls, message: str):
        discord_response = DiscordResponse()
        discord_response.type = ResponseType.CHANNEL_MESSAGE
        discord_response.content = message
        return discord_response

    @classmethod
    def channel_message_with_source(cls, message: str):
        discord_response = DiscordResponse()
        discord_response.type = ResponseType.CHANNEL_MESSAGE_WITH_SOURCE
        discord_response.content = message
        return discord_response

    @classmethod
    def acknowledge_with_source(cls):
        discord_response = DiscordResponse()
        discord_response.type = ResponseType.ACKNOWLEDGE_WITH_SOURCE
        return discord_response
