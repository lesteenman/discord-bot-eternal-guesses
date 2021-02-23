import pytest

from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.repositories.configs_repository import ConfigsRepositoryImpl
from tests.integration.conftest import TABLE_NAME, HOST

pytestmark = pytest.mark.asyncio


async def test_get_unknown_guild_returns_empty_config():
    # Given
    configs_repository = ConfigsRepositoryImpl(table_name=TABLE_NAME, host=HOST)
    guild_id = 12000

    # When
    config = configs_repository.get(guild_id)

    # Then
    assert config.guild_id == guild_id
    assert config.management_channels == []
    assert config.management_roles == []


async def test_get_guild():
    # Given
    configs_repository = ConfigsRepositoryImpl(table_name=TABLE_NAME, host=HOST)

    guild_id = 12000
    management_channel_1 = 1000
    management_channel_2 = 1002
    management_role = 3000
    guild_config = GuildConfig(
        guild_id=guild_id,
        management_channels=[management_channel_1, management_channel_2],
        management_roles=[management_role]
    )

    # When
    configs_repository.save(guild_config)
    retrieved_config = configs_repository.get(guild_id)

    # Then
    assert retrieved_config.guild_id == guild_id

    assert len(retrieved_config.management_channels) == 2
    assert management_channel_1 in retrieved_config.management_channels
    assert management_channel_2 in retrieved_config.management_channels

    assert retrieved_config.management_roles == [management_role]
