import re
from abc import ABC

from eternal_guesses.model.data.guild_config import GuildConfig

PK_REGEX = r"GUILD#(.*)"


def _hash_key(guild_id: int):
    return f"GUILD#{guild_id}"


def _range_key():
    return "CONFIG"


def _config_from_model(model: dict) -> GuildConfig:
    guild_id = int(re.match(PK_REGEX, model['pk']).group(1))
    guild_config = GuildConfig(guild_id)

    for channel in model.get('management_channels', []):
        guild_config.management_channels.append(channel)

    for role in model.get('management_roles', []):
        guild_config.management_roles.append(role)

    return guild_config


class ConfigsRepository(ABC):
    def get(self, guild_id: int) -> GuildConfig:
        pass

    def save(self, guild_config: GuildConfig):
        pass


class ConfigsRepositoryImpl(ConfigsRepository):
    def __init__(self, eternal_guesses_table):
        self.table = eternal_guesses_table

    def get(self, guild_id: int) -> GuildConfig:
        result = self.table.get_item(
            Key={
                'pk': _hash_key(guild_id),
                'sk': _range_key(),
            },
        )

        if 'Item' not in result:
            return GuildConfig(guild_id)

        return _config_from_model(result['Item'])

    def save(self, guild_config: GuildConfig):
        model = {
            'pk': _hash_key(guild_config.guild_id),
            'sk': _range_key(),
            'management_channels': list(
                int(channel) for channel in guild_config.management_channels
            ),
            'management_roles': list(
                int(role) for role in guild_config.management_roles
            )
        }

        self.table.put_item(Item=model)
