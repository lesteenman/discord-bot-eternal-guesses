import contextlib
import logging
from abc import ABC

import discord

from eternal_guesses.util.config import load_config
from eternal_guesses.model.discord_member import DiscordMember

log = logging.getLogger(__name__)


class DiscordMessaging(ABC):
    async def create_channel_message(self, channel_id: int, text: str) -> int:
        pass

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        pass

    async def send_dm(self, member: DiscordMember, message: str):
        pass


class DiscordMessagingImpl(DiscordMessaging):
    async def create_channel_message(self, channel_id: int, text: str) -> int:
        async with self._discord_client() as client:
            log.info("Posting a new channel message")
            log.debug(
                f"Creating a new channel message, channel_id={channel_id}, text={text}")

            text_channel = await client.fetch_channel(channel_id)

            channel_message = await text_channel.send(content=text)
            log.debug(f"channel message id = {channel_message.id}")

            return channel_message.id

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        async with self._discord_client() as client:
            log.info("Posting a new channel message")
            log.debug(
                f"Creating a new channel message, channel_id={channel_id}, message_id={message_id}, text={text}")

            text_channel = await client.fetch_channel(channel_id)

            real_message_id = 804804560538304583
            log.info(f"Is this the message? {message_id == real_message_id}")
            message = await text_channel.fetch_message(message_id)

            await message.edit(content=text)
            log.debug("updated channel message")

    async def send_dm(self, member: DiscordMember, message: str):
        async with self._discord_client() as client:
            log.info("Fetching user")
            user = await client.fetch_user(member.user_id)

            await user.send(message)

    @contextlib.asynccontextmanager
    async def _discord_client(self) -> discord.Client:
        client = discord.Client()
        config = load_config()
        await client.login(config.discord_bot_token)

        try:
            yield client
        finally:
            await client.close()
