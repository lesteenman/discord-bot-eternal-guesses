import contextlib
import logging

import discord
from eternal_guesses.config import load_config
from eternal_guesses.model.discord_event import DiscordMember

log = logging.getLogger(__name__)


async def create_channel_message(channel_id: int, text: str) -> int:
    async with discord_client() as client:
        log.info("Posting a new channel message")
        log.debug(f"Creating a new channel message, channel_id={channel_id}, text={text}")

        text_channel = await client.fetch_channel(channel_id)

        channel_message_id = await text_channel.send(content=text)
        log.debug(f"channel message id = {channel_message_id}")

        return channel_message_id


async def update_channel_message(channel_id: int, message_id: int, text: str):
    async with discord_client() as client:
        log.info("Posting a new channel message")
        log.debug(f"Creating a new channel message, channel_id={channel_id}, text={text}")

        text_channel = await client.fetch_channel(channel_id)

        message = await text_channel.fetch_message(message_id)

        await message.edit(content=text)
        log.debug(f"updated channel message")


async def send_dm(member: DiscordMember, message: str):
    async with discord_client() as client:
        log.info("Fetching user")
        user = await client.fetch_user(member.user_id)

        await user.send(message)


@contextlib.asynccontextmanager
async def discord_client() -> discord.Client:
    client = discord.Client()
    config = load_config()
    await client.login(config.discord_bot_token)

    try:
        yield client
    finally:
        await client.close()
