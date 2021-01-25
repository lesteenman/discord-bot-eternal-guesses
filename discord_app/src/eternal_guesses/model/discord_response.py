class DiscordResponse(object):
    type: int
    content: str = None

    def json(self):
        if self.type == 3 or self.type == 4:
            return {
                'type': self.type,
                'data': {
                    'content': self.content
                }
            }
        else:
            return {
                'type': self.type
            }

    @classmethod
    def pong(cls):
        discord_response = DiscordResponse()
        discord_response.type = 1
        return discord_response

    @classmethod
    def acknowledge(cls):
        discord_response = DiscordResponse()
        discord_response.type = 2
        return discord_response

    @classmethod
    def channel_message(cls, message: str):
        discord_response = DiscordResponse()
        discord_response.type = 3
        discord_response.content = message
        return discord_response

    @classmethod
    def channel_message_with_source(cls, message: str):
        discord_response = DiscordResponse()
        discord_response.type = 4
        discord_response.content = message
        return discord_response

    @classmethod
    def acknowledge_with_source(cls):
        discord_response = DiscordResponse()
        discord_response.type = 5
        return discord_response
