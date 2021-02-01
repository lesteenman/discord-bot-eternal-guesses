import logging
from pprint import pformat

import boto3
from eternal_guesses.config import load_config
from eternal_guesses.model.data.guild_config import GuildConfig

log = logging.getLogger(__name__)


def empty_config(guild_id):
    config = GuildConfig()
    config.guild_id = guild_id
    return config


def make_config(guild_id, item) -> GuildConfig:
    config = empty_config(guild_id)

    for channel in item['management_channels']:
        config.management_channels.append(channel)

    for role in item['management_roles']:
        config.management_roles.append(role)

    return config


class ConfigsRepository:
    @staticmethod
    def get(guild_id: int) -> GuildConfig:
        table = ConfigsRepository._get_table()

        key = {
            "pk": f"GUILD#{guild_id}",
            "sk": "CONFIG",
        }

        log.debug(f"getting item, key={key}")

        response = table.get_item(Key=key)

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"table.get_item response: {pformat(response)}")

        if 'Item' not in response:
            return empty_config(guild_id)

        item = response['Item']
        return make_config(guild_id, item)

    @staticmethod
    def save(config: GuildConfig):
        assert config.guild_id is not None

        table = ConfigsRepository._get_table()

        item = {
            "pk": f"GUILD#{config.guild_id}",
            "sk": "CONFIG",
            "management_channels": config.management_channels,
            "management_roles": config.management_roles,
        }

        log.debug(f"saving item, item={item}")

        response = table.put_item(
            Item=item
        )

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"table.put_item response: {pformat(response)}")

    @staticmethod
    def _get_table():
        dynamodb = boto3.resource('dynamodb')
        config = load_config()
        table = dynamodb.Table(config.dynamodb_table_name)
        return table
