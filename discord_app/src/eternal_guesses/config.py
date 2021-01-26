import os

from eternal_guesses.model.data.config import Config


def load_config() -> Config:
    config = Config()

    config.discord_public_key = os.getenv('DISCORD_PUBLIC_KEY')
    config.discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
    config.dynamodb_table_name = os.getenv('DYNAMODB_TABLE_NAME')

    return config
