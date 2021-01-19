import contextlib
import logging
import os

import discord

log = logging.getLogger()
log.setLevel(logging.DEBUG)


async def send_dm(user_id: int, message: str):
    async with discord_client() as client:
        print("Fetching user")
        user = await client.fetch_user(user_id)

        await user.send(message)


@contextlib.asynccontextmanager
async def discord_client() -> discord.Client:
    client = discord.Client()
    await client.login(os.getenv('DISCORD_BOT_TOKEN'))

    try:
        yield client
    finally:
        await client.close()
