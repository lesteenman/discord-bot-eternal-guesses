import json
from unittest.mock import patch

from discord_interactions import InteractionType
from eternal_guesses import handler


@patch('discord_interactions.verify_key')
@patch('handlers.ping.call')
def test_handle_ping(mock_handler_ping, mock_verify_key):
    # Given
    mock_verify_key.return_value = True
    mock_handler_ping.return_value = {'type': InteractionType.PING}

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
    mock_handler_ping.assert_called_with(body)
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == body


@patch('discord_interactions.verify_key')
def test_unauthorized_request(mock_verify_key):
    # Given
    mock_verify_key.return_value = False

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
