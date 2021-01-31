import json
from unittest.mock import patch

from eternal_guesses import api_authorizer
from eternal_guesses.api_authorizer import AuthorizationResult


@patch.object(api_authorizer.discord_interactions, 'verify_key', autospec=True)
def test_pass(mock_verify_key):
    # Given
    mock_verify_key.return_value = True

    event = {
        'body': json.dumps({}),
        'headers': {
            'x-signature-ed25519': 'ABC',
            'x-signature-timestamp': '1000000',
        }
    }

    # When
    result, response = api_authorizer.authorize(event)

    # Then
    assert result == AuthorizationResult.PASS


@patch.object(api_authorizer.discord_interactions, 'verify_key', autospec=True)
def test_fail(mock_verify_key):
    # Given
    mock_verify_key.return_value = False

    event = {
        'body': json.dumps({}),
        'headers': {
            'x-signature-ed25519': 'ABC',
            'x-signature-timestamp': '1000000',
        }
    }

    # When
    result, response = api_authorizer.authorize(event)

    # Then
    assert result == AuthorizationResult.FAIL
    assert response.status_code == 401
