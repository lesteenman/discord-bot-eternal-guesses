import json
from unittest.mock import patch

from eternal_guesses import handler
from eternal_guesses.authorizer import AuthorizationResult
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.lambda_response import LambdaResponse


@patch('eternal_guesses.authorizer.authorize')
def test_unauthorized_request(mock_authorize):
    # Given
    mock_authorize.return_value = (AuthorizationResult.FAIL, LambdaResponse.unauthorized("key does not check out"))

    body = {'type': 1}
    event = {
        'body': json.dumps(body),
        'headers': {
            'x-signature-ed25519': '',
            'x-signature-timestamp': '',
        }
    }
    context = {}

    # When
    response = handler.handle_lambda(event, context)

    # Then
    assert response['statusCode'] == 401


@patch('eternal_guesses.authorizer.authorize')
@patch('eternal_guesses.model.discord_event')
@patch('eternal_guesses.router.route')
def test_authorized_request(mock_router, mock_discord_event, mock_authorize):
    # Given
    mock_authorize.return_value = (AuthorizationResult.PASS, None)
    mock_router.return_value = LambdaResponse.success({'response': 'mocked'})
    mock_discord_event.from_event.return_value = None

    event = {
        'body': json.dumps({'type': 1}),
        'headers': {
            'x-signature-ed25519': '',
            'x-signature-timestamp': '',
        }
    }

    # When
    response = handler.handle_lambda(event, {})

    # Then
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == {'response': 'mocked'}


@patch('eternal_guesses.authorizer.authorize')
@patch('eternal_guesses.model.discord_event.from_event')
@patch('eternal_guesses.router.route')
def test_discord_event(mock_router, mock_from_event, mock_authorize):
    # Given
    mock_authorize.return_value = (AuthorizationResult.PASS, None)
    mock_router.return_value = LambdaResponse.success({'response': 'mocked'})

    event_body = {'type': 1}

    discord_event = DiscordEvent()
    mock_from_event.return_value = discord_event

    event = {
        'body': json.dumps(event_body),
        'headers': {
            'x-signature-ed25519': '',
            'x-signature-timestamp': '',
        }
    }
    context = {}

    # When
    handler.handle_lambda(event, context)

    # Then
    mock_router.assert_called_with(discord_event)

