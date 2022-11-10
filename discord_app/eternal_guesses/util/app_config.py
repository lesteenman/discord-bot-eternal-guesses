import os
import typing


def discord_public_key() -> str:
    return os.getenv('DISCORD_PUBLIC_KEY')


def discord_bot_token() -> str:
    return os.getenv('DISCORD_BOT_TOKEN')


def dynamodb_table_name() -> str:
    return os.getenv('DYNAMODB_TABLE_NAME')


def aws_endpoint_url() -> typing.Optional[str]:
    return os.getenv('AWS_ENDPOINT_URL', None)
