from aws_cdk import (Stack, Duration, aws_lambda, aws_apigateway, aws_dynamodb,
                     aws_sns, aws_logs, aws_logs_destinations)
from aws_cdk.aws_dynamodb import ITable
from aws_cdk.aws_lambda import Function, Runtime
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_sns import Topic
from constructs import Construct

from infra import config


class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.config = config.config

        dynamodb_table = self.create_table()
        discord_app_handler = self.create_app_handler(dynamodb_table.table_name)
        self.grant_table_readwrite_permissions(dynamodb_table, discord_app_handler)

        self.create_api(discord_app_handler)

        self.setup_app_error_alerting(discord_app_handler)

    def create_table(self) -> aws_dynamodb.ITable:
        partition_key = aws_dynamodb.Attribute(
            name="pk",
            type=aws_dynamodb.AttributeType.STRING
        )

        sort_key = aws_dynamodb.Attribute(
            name="sk",
            type=aws_dynamodb.AttributeType.STRING
        )

        return aws_dynamodb.Table(self, "EternalGuessesTable",
                                  partition_key=partition_key,
                                  sort_key=sort_key,
                                  billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
                                  )

    def create_app_handler(self, dynamodb_table_name: str) -> Function:
        environment = {
            'DISCORD_PUBLIC_KEY': self.config['DISCORD_PUBLIC_KEY'],
            'DISCORD_BOT_TOKEN': self.config['DISCORD_BOT_TOKEN'],
            'DYNAMODB_TABLE_NAME': dynamodb_table_name,
            'LOGURU_LEVEL': self.config['APP_LOG_LEVEL'],
        }

        return PythonFunction(
            self, "DiscordAppFunction",
            runtime=Runtime.PYTHON_3_9,
            timeout=Duration.seconds(10),
            memory_size=1024,
            entry="../discord_app",
            index="eternal_guesses/handler.py",
            handler="handle_lambda",
            environment=environment
        )

    def grant_table_readwrite_permissions(self, dynamodb_table: ITable, function: Function):
        dynamodb_table.grant_full_access(function)
        # dynamodb_table.grant(function, "dynamodb:DescribeTable")

    def create_api(self, discord_app_handler: Function):
        api = aws_apigateway.RestApi(self, "eternal-guesses-api",
                                     rest_api_name="Eternal Guesses API")
        discord_app_integration = aws_apigateway.LambdaIntegration(discord_app_handler)
        discord_resource = api.root.add_resource("discord")
        discord_resource.add_method("POST", discord_app_integration)

    def setup_app_error_alerting(self, function_to_monitor: Function) -> None:
        app_errors_sns_topic = self.create_sns_topic()
        cloudwatch_logs_handler = self.create_logs_handler(app_errors_sns_topic)

        self.subscribe_handler_to_function_logs(function_to_monitor, cloudwatch_logs_handler)
        self.subscribe_emails_to_topic(app_errors_sns_topic, self.config['NOTIFICATION_EMAIL'])

    def create_sns_topic(self) -> Topic:
        sns_topic = aws_sns.Topic(self, "eternal-guess-error-topic")
        return sns_topic

    def subscribe_emails_to_topic(self, sns_topic: Topic, email_address: str) -> None:
        aws_sns.Subscription(self, "eternal-guess-error-subscription",
                             topic=sns_topic,
                             protocol=aws_sns.SubscriptionProtocol.EMAIL,
                             endpoint=email_address)

    def create_logs_handler(self, topic: Topic) -> Function:
        environment = {
            'snsARN': topic.topic_arn,
        }

        logs_handler = PythonFunction(self, "eternal-guess-logs-parser",
                                      runtime=aws_lambda.Runtime.PYTHON_3_9,
                                      entry="../error_parser_function",
                                      index="parser.py",
                                      handler="lambda_handler",
                                      environment=environment)

        topic.grant_publish(logs_handler)

        return logs_handler

    def subscribe_handler_to_function_logs(self, app_handler, logs_handler):
        aws_logs.SubscriptionFilter(self, "eternal-guess-handler-subscription-filter",
                                    log_group=app_handler.log_group,
                                    destination=aws_logs_destinations.LambdaDestination(logs_handler),
                                    filter_pattern=aws_logs.FilterPattern.any_term("ERROR", "WARNING"))
