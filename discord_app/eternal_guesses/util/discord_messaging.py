import contextlib
from abc import ABC

import discord
from discord import AllowedMentions
from loguru import logger

from eternal_guesses.util import app_config


class DiscordMessaging(ABC):
    async def send_channel_message(self, channel_id: int, text: str = None, embed: discord.Embed = None) -> int:
        raise NotImplementedError()

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        raise NotImplementedError()


class DiscordMessagingImpl(DiscordMessaging):
    async def send_channel_message(self, channel_id: int, text: str = None, embed: discord.Embed = None) -> int:
        logger.debug(f"send_channel_message, channel_id={channel_id}, text='{text}'")
        async with self._discord_client() as client:
            logger.info("Posting a new channel message")
            logger.debug(
                f"Creating a new channel message, channel_id={channel_id}, text={text}")

            text_channel = await client.fetch_channel(channel_id)

            channel_message = await text_channel.send(
                content=text,
                embed=embed,
                allowed_mentions=AllowedMentions.none(),
            )
            logger.debug(f"channel message id = {channel_message.id}")

            return channel_message.id

    async def update_channel_message(self, channel_id: int, message_id: int, text: str):
        logger.debug(f"update_channel_message, channel_id={channel_id}, message_id={message_id}, text='{text}'")
        async with self._discord_client() as client:
            logger.info("Posting a new channel message")
            logger.debug(
                f"Creating a new channel message, channel_id={channel_id}, message_id={message_id}, text={text}")

            text_channel = await client.fetch_channel(channel_id)

            message = await text_channel.fetch_message(message_id)

            await message.edit(content=text, allowed_mentions=AllowedMentions.none())
            logger.debug("updated channel message")

    @contextlib.asynccontextmanager
    async def _discord_client(self) -> discord.Client:
        client = discord.Client()
        await client.login(app_config.discord_bot_token)

        try:
            yield client
        finally:
            await client.close()