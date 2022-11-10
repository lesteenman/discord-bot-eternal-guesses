import os
from typing import Dict

import boto3
import discord
import docker
import opnieuw
import pytest
from botocore.exceptions import ClientError
from loguru import logger

from eternal_guesses.authorization.api_authorizer import ApiAuthorizer, \
    AuthorizationResult
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.lambda_response import LambdaResponse
# from eternal_guesses.repositories.dynamodb_models import EternalGuessesTable
from eternal_guesses.util.discord_messaging import DiscordMessaging

# from pynamodb.exceptions import TableError

REGION = "eu-west-1"
TABLE_NAME = "eternal-guesses-test"
DYNAMODB_HOST = "http://127.0.0.1:8000"
ACCESS_KEY_ID = "LOCAL"


@pytest.fixture(scope="session", autouse=True)
def start_dynamodb_container():
    docker_client = docker.from_env()
    dynamodb_container = docker_client.containers.run('amazon/dynamodb-local', ports={8000: 8000}, detach=True,
                                                      auto_remove=True)

    yield

    dynamodb_container.stop()


@pytest.fixture(autouse=True)
def dynamodb_resource(monkeypatch):
    monkeypatch.setenv('AWS_ENDPOINT_URL', DYNAMODB_HOST)
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', ACCESS_KEY_ID)
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', "BOGUS")
    monkeypatch.setenv('AWS_DEFAULT_REGION', REGION)

    yield boto3.resource(
        'dynamodb',
        endpoint_url=DYNAMODB_HOST,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key="BOGUS",
        region_name=REGION,
    )


@opnieuw.retry(retry_on_exceptions=ClientError, max_calls_total=10, retry_window_after_first_call_in_seconds=10)
def _create_table(dynamodb, table_name):
    return dynamodb.create_table(
        TableName=table_name,
        BillingMode='PAY_PER_REQUEST',
        KeySchema=[
            {
                "AttributeName": "pk",
                "KeyType": "HASH",
            },
            {
                "AttributeName": "sk",
                "KeyType": "RANGE",
            },
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "pk",
                "AttributeType": "S",
            },
            {
                "AttributeName": "sk",
                "AttributeType": "S",
            },
        ],
    )


@opnieuw.retry(retry_on_exceptions=ClientError, max_calls_total=10, retry_window_after_first_call_in_seconds=5)
def _delete_table(table):
    table.delete()


@pytest.fixture(autouse=True)
def eternal_guesses_table(dynamodb_resource, monkeypatch):
    monkeypatch.setenv('DYNAMODB_TABLE_NAME', TABLE_NAME)
    table = _create_table(dynamodb_resource, TABLE_NAME)

    yield table

    _delete_table(table)


@pytest.fixture(autouse=True)
def fixed_authorization_result(mocker):
    class PassingTestAuthorizer(ApiAuthorizer):
        def authorize(self, event: Dict) -> (AuthorizationResult, LambdaResponse):
            return AuthorizationResult.PASS, None

    test_authorizer = PassingTestAuthorizer()
    mocker.patch('eternal_guesses.util.injector._api_authorizer', return_value=test_authorizer)


@pytest.fixture(autouse=True)
def stub_discord_messaging(mocker):
    class SilentDiscordMessaging(DiscordMessaging):
        async def send_channel_message(
            self, channel_id: int, text: str = None,
            embed: discord.Embed = None, view: discord.ui.View = None
        ) -> int:
            logger.info(
                f"[stub send_channel_message] channel_id={channel_id}, text={text}, embed={embed}, view={view}"
            )
            return 1

        async def update_channel_message(
            self, channel_id: int, message_id: int, text: str = None,
            embed: discord.Embed = None, view: discord.ui.View = None
        ):
            logger.info(
                f"[stub update_channel_emssage] channel_id={channel_id}, message_id={message_id} text={text},"
                f"embed={embed}, view={view}"
            )
            pass

        async def send_dm(self, member: DiscordMember, text: str):
            logger.info(
                f"[stub send_dm] member_id={member.user_id} text={text}"
            )
            pass

    silent_discord_messaging = SilentDiscordMessaging()
    mocker.patch('eternal_guesses.util.injector._discord_messaging', return_value=silent_discord_messaging)


@pytest.fixture(autouse=True)
def disable_xray():
    os.environ['AWS_XRAY_SDK_ENABLED'] = 'false'
