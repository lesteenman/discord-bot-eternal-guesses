import logging
import re
from abc import ABC

from pynamodb.exceptions import DoesNotExist

from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.repositories.dynamodb_models import EternalGuessesTable

log = logging.getLogger(__name__)

PK_REGEX = r"GUILD#(.*)"


def _hash_key(guild_id: int):
    return f"GUILD#{guild_id}"


def _range_key():
    return "CONFIG"


def _config_from_model(model: EternalGuessesTable) -> GuildConfig:
    guild_id = int(re.match(PK_REGEX, model.pk).group(1))
    config = GuildConfig(guild_id)

    for channel in model.management_channels:
        config.management_channels.append(channel)

    for role in model.management_roles:
        config.management_roles.append(role)

    return config


class ConfigsRepository(ABC):
    def get(self, guild_id: int) -> GuildConfig:
        pass

    def save(self, guild_config: GuildConfig):
        pass


class ConfigsRepositoryImpl(ConfigsRepository):
    def __init__(self, table_name: str = None, host: str = None):
        self.table = EternalGuessesTable

        if table_name is not None:
            self.table.Meta.table_name = table_name

        if host is not None:
            self.table.Meta.host = host

    def get(self, guild_id: int) -> GuildConfig:
        try:
            model = self.table.get(_hash_key(guild_id), _range_key())
        except DoesNotExist:
            return GuildConfig(guild_id)

        return _config_from_model(model)

    def save(self, guild_config: GuildConfig):
        model = self.table(_hash_key(guild_config.guild_id), _range_key())

        model.management_channels = list(int(channel) for channel in guild_config.management_channels)
        model.management_roles = list(int(role) for role in guild_config.management_roles)

        model.save()
