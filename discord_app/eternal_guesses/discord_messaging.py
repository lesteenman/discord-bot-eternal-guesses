import contextlib
from abc import ABC

import discord
from loguru import logger

from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.util import app_config


class DiscordMessaging(ABC):
    async def send_channel_message(self, channel_id: int, text: str) -> int:
        logger.warning("Using an ABC method!")
        pass

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        logger.warning("Using an ABC method!")
        pass

    async def send_dm(self, member: DiscordMember, text: str):
        logger.warning("Using an ABC method!")
        pass

    async def send_temp_message(self, channel_id: int, text: str, timeout: int = 30):
        logger.warning("Using an ABC method!")
        pass


class DiscordMessagingImpl(DiscordMessaging):
    async def send_channel_message(self, channel_id: int, text: str) -> int:
        logger.debug(f"send_channel_message, channel_id={channel_id}, text='{text}'")
        async with self._discord_client() as client:
            logger.info("Posting a new channel message")
            logger.debug(
                f"Creating a new channel message, channel_id={channel_id}, text={text}")

            text_channel = await client.fetch_channel(channel_id)

            channel_message = await text_channel.send(content=text, allowed_mentions={'parse': []})
            logger.debug(f"channel message id = {channel_message.id}")

            return channel_message.id

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        logger.debug(f"update_channel_message, channel_id={channel_id}, message_id={message_id}, text='{text}'")
        async with self._discord_client() as client:
            logger.info("Posting a new channel message")
            logger.debug(
                f"Creating a new channel message, channel_id={channel_id}, message_id={message_id}, text={text}")

            text_channel = await client.fetch_channel(channel_id)

            real_message_id = 804804560538304583
            logger.info(f"Is this the message? {message_id == real_message_id}")
            message = await text_channel.fetch_message(message_id)

            await message.edit(content=text, allowed_mentions={'parse': []})
            logger.debug("updated channel message")

    async def send_dm(self, member: DiscordMember, text: str):
        logger.debug(f"send_dm to {member.user_id}, text='{text}'")
        async with self._discord_client() as client:
            logger.info("Fetching user")
            user = await client.fetch_user(member.user_id)

            await user.send(text)

    async def send_temp_message(self, channel_id: int, text: str, timeout: int = 30):
        logger.debug(f"Sending a temp message to {channel_id}, timeout={timeout}, text='{text}'")
        async with self._discord_client() as client:
            text_channel = await client.fetch_channel(channel_id)

            await text_channel.send(content=text, delete_after=timeout)

    @contextlib.asynccontextmanager
    async def _discord_client(self) -> discord.Client:
        client = discord.Client()
        await client.login(app_config.discord_bot_token)

        try:
            yield client
        finally:
            await client.close()
