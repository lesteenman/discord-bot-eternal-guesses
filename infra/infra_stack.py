from aws_cdk import (core, aws_lambda, aws_apigateway)


class InfraStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        discord_app_handler = aws_lambda.Function(self, "DiscordAppFunction",
                                                  runtime=aws_lambda.Runtime.PYTHON_3_8,
                                                  code=aws_lambda.Code.from_asset(
                                                      "../discord_app/.build/deployment.zip"),
                                                  handler="handler.handle_lambda")

        api = aws_apigateway.RestApi(self, "eternal-guesses-api",
                                     rest_api_name="Eternal Guesses API")

        discord_app_integration = aws_apigateway.LambdaIntegration(discord_app_handler)

        discord_resource = api.root.add_resource("discord")
        discord_resource.add_method("POST", discord_app_integration)
