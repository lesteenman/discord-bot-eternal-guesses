import json
from typing import Dict

from aws_cdk import (core, aws_lambda, aws_apigateway, aws_dynamodb)


def read_config() -> Dict:
    with open('../app_config.json', 'r') as env_file:
        return json.loads(env_file.read())


class InfraStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = read_config()

        dynamodb_table = aws_dynamodb.Table(self, "EternalGuessesTable",
                                            partition_key=aws_dynamodb.Attribute(
                                                name="pk",
                                                type=aws_dynamodb.AttributeType.STRING
                                            ),
                                            sort_key=aws_dynamodb.Attribute(
                                                name="sk",
                                                type=aws_dynamodb.AttributeType.STRING
                                            ),
                                            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST)

        discord_app_handler = aws_lambda.Function(self, "DiscordAppFunction",
                                                  runtime=aws_lambda.Runtime.PYTHON_3_8,
                                                  timeout=core.Duration.seconds(10),
                                                  memory_size=1024,
                                                  code=aws_lambda.Code.from_asset(
                                                      "../discord_app/dist/eternal_guesses-0.1.0.zip"),
                                                  handler="eternal_guesses.handler.handle_lambda",
                                                  environment={
                                                      'DISCORD_PUBLIC_KEY': config['DISCORD_PUBLIC_KEY'],
                                                      'DISCORD_BOT_TOKEN': config['DISCORD_BOT_TOKEN'],
                                                      'DYNAMODB_TABLE_NAME': dynamodb_table.table_name,
                                                  })

        dynamodb_table.grant_read_write_data(discord_app_handler)

        api = aws_apigateway.RestApi(self, "eternal-guesses-api",
                                     rest_api_name="Eternal Guesses API")

        discord_app_integration = aws_apigateway.LambdaIntegration(discord_app_handler)

        discord_resource = api.root.add_resource("discord")
        discord_resource.add_method("POST", discord_app_integration)
