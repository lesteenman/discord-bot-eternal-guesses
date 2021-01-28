import contextlib

import discord
from config import load_config
from model.discord_event import DiscordMember


async def create_channel_message(channel_id: int, text: str) -> int:
    pass


async def update_channel_message(message_id: int, text: str):
    pass


async def send_dm(member: DiscordMember, message: str):
    async with discord_client() as client:
        print("Fetching user")
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
