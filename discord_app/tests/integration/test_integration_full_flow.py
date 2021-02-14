import json

from eternal_guesses import handler
from eternal_guesses.config import load_config
from tests.integration.helpers import create_admin_event, create_context

app_config = load_config()


def test_integration_full_flow():
    pass # TODO
    # mocker.patch.object(handler.api_authorizer, 'authorize', return_value=(AuthorizationResult.PASS, None))
    #
    # calling_admin_info_does_not_except()
    #
    # all_games = integration_db.find_games()
    # assert len(all_games) == 0


def calling_admin_info_does_not_except():
    # When we get the admin info
    response = handler.handle_lambda(
        create_admin_event(subcommand='info'),
        create_context())

    # Then we get some json back
    response_body = json.loads(response['body'])
    assert response_body is not None


# @pytest.fixture
# def use_moto():
#     print("USE MOTO FIXTURE CALLED!")
#
#     @mock_dynamodb2
#     def dynamodb_client():
#         dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
#
#         dynamodb.create_table(
#             TableName=app_config.dynamodb_table_name,
#             KeySchema=[
#                 {
#                     'AttributeName': 'pk',
#                     'KeyType': 'HASH',
#                 },
#                 {
#                     'AttributeName': 'sk',
#                     'KeyType': 'RANGE',
#                 },
#             ],
#             AttributeDefinitions=[
#                 {
#                     'AttributeName': 'pk',
#                     'AttributeType': 'S',
#                 },
#                 {
#                     'AttributeName': 'sk',
#                     'AttributeType': 'S',
#                 },
#             ],
#             BillingMode='PAY_PER_REQUEST',
#         )
#
#         return dynamodb
#
#     return dynamodb_client
