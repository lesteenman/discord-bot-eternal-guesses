from unittest.mock import patch

import pytest
from eternal_guesses.repositories import configs_repository
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from model.data.guild_config import GuildConfig

pytestmark = pytest.mark.asyncio


def create_mock_dynamodb(mocker, return_value=None):
    mock_table = mocker.MagicMock()
    if return_value is not None:
        mock_table.get_item.return_value = return_value

    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    return mock_dynamodb


@patch.object(configs_repository, 'boto3', autospec=True)
async def test_get_unknown_guild_returns_empty_config(mock_boto_3, mocker):
    # Given
    guild_id = 12000

    table_get_return_value = {
        'ResponseMetadata': {},
    }

    mock_boto_3.resource.return_value = create_mock_dynamodb(
        mocker, return_value=table_get_return_value)

    # When
    config = ConfigsRepository.get(guild_id)

    # Then
    assert config.guild_id == guild_id
    assert config.management_channels == []
    assert config.management_roles == []


@patch.object(configs_repository, 'boto3', autospec=True)
async def test_get_guild(mock_boto_3, mocker):
    # Given
    guild_id = 12000
    management_channel_1 = 1000
    management_channel_2 = 1000
    management_role = 3000

    table_get_return_value = {
        'ResponseMetadata': {},
        'Item': {
            'management_channels': [management_channel_1, management_channel_2],
            'management_roles': [management_role],
        }
    }
    mock_boto_3.resource.return_value = create_mock_dynamodb(
        mocker, return_value=table_get_return_value)

    # When
    config = ConfigsRepository.get(guild_id)

    # Then
    assert config.guild_id == guild_id

    assert len(config.management_channels) == 2
    assert management_channel_1 in config.management_channels
    assert management_channel_2 in config.management_channels

    assert config.management_roles == [management_role]


@patch.object(configs_repository, 'boto3', autospec=True)
def test_save_config(mock_boto_3, mocker):
    # Given
    guild_id = 12000
    management_role_1 = 1000
    management_role_2 = 2000
    management_role_3 = 2000
    management_channel = 50000

    mock_table = mocker.MagicMock()
    mock_dynamodb = mocker.MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_boto_3.resource.return_value = mock_dynamodb

    config = GuildConfig()
    config.guild_id = guild_id
    config.management_channels = [management_channel]
    config.management_roles = [
        management_role_1,
        management_role_2,
        management_role_3,
    ]

    # When
    ConfigsRepository.save(config)

    # Then
    mock_table.put_item.assert_called_with(Item={
        'pk': f"GUILD#{guild_id}",
        'sk': "CONFIG",
        'management_channels': [management_channel],
        'management_roles': [management_role_1, management_role_2, management_role_3],
    })
