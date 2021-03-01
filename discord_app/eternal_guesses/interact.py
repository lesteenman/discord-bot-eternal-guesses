import contextlib
import logging

import discord

from eternal_guesses.util import app_config

log = logging.getLogger()
log.setLevel(logging.DEBUG)


async def send_dm(user_id: int, message: str):
    async with discord_client() as client:
        log.info("Fetching user")
        user = await client.fetch_user(user_id)

        await user.send(message)


@contextlib.asynccontextmanager
async def discord_client() -> discord.Client:
    client = discord.Client()
    await client.login(app_config.discord_bot_token)

    try:
        yield client
    finally:
        await client.close()
