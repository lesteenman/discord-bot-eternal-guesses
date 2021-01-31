import json
from typing import Dict

from aws_cdk import (core, aws_lambda, aws_apigateway, aws_dynamodb, aws_sns, aws_logs, aws_logs_destinations)


def read_config() -> Dict:
    with open('../app_config.json', 'r') as env_file:
        return json.loads(env_file.read())


class InfraStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = read_config()

        dynamodb_table = self.create_table()

        discord_app_handler = self.create_app_handler(config, dynamodb_table)

        dynamodb_table.grant_read_write_data(discord_app_handler)

        self.create_api(discord_app_handler)

        error_monitor = self.create_error_monitor(config)
        self.monitor_logs(discord_app_handler, error_monitor)

    def create_error_monitor(self, config: Dict):
        sns_topic = aws_sns.Topic(self, "eternal-guess-error-topic")
        aws_sns.Subscription(self, "eternal-guess-error-subscription",
                                            topic=sns_topic,
                                            protocol=aws_sns.SubscriptionProtocol.EMAIL,
                                            endpoint=config['NOTIFICATION_EMAIL'])

        cloudwatch_logs_parser = aws_lambda.Function(self, "eternal-guess-logs-parser",
                                                     runtime=aws_lambda.Runtime.PYTHON_3_7,
                                                     code=aws_lambda.Code.from_asset(
                                                         "../error_parser_function/dist/error_parser_function.zip"),
                                                     handler="parser.lambda_handler",
                                                     environment={
                                                         'snsARN': sns_topic.topic_arn,
                                                     })

        sns_topic.grant_publish(cloudwatch_logs_parser)

        return cloudwatch_logs_parser

    def monitor_logs(self, app_handler, error_monitor):
        aws_logs.SubscriptionFilter(self, "eternal-guess-handler-subscription-filter",
                                    log_group=app_handler.log_group,
                                    destination=aws_logs_destinations.LambdaDestination(error_monitor),
                                    filter_pattern=aws_logs.FilterPattern.any_term("ERROR", "WARNING", "500"))

    def create_api(self, discord_app_handler):
        api = aws_apigateway.RestApi(self, "eternal-guesses-api",
                                     rest_api_name="Eternal Guesses API")
        discord_app_integration = aws_apigateway.LambdaIntegration(discord_app_handler)
        discord_resource = api.root.add_resource("discord")
        discord_resource.add_method("POST", discord_app_integration)

    def create_app_handler(self, config, dynamodb_table):
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
        return discord_app_handler

    def create_table(self):
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
        return dynamodb_table
