from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.model.discord_event import DiscordMember


class FakeDiscordMessaging(DiscordMessaging):
    def __init__(self):
        self.updated_channel_messages = []
        self.sent_dms = []
        self.sent_channel_messages = []
        self.created_channel_message_id = 0

    async def create_channel_message(self, channel_id: int, text: str) -> int:
        self.sent_channel_messages.append({'channel_id': channel_id, 'text': text})
        return self.created_channel_message_id

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        self.updated_channel_messages.append({'channel_id': channel_id, 'message_id': message_id, 'text': text})

    async def send_dm(self, member: DiscordMember, message: str):
        self.sent_dms.append({'member': member, 'text': message})
