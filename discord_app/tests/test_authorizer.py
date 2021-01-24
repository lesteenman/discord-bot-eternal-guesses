import json
from unittest.mock import patch

import authorizer
from authorizer import AuthorizationResult


@patch('discord_interactions.verify_key')
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
    result, response = authorizer.authorize(event)

    # Then
    assert result == AuthorizationResult.PASS


@patch('discord_interactions.verify_key')
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
    result, response = authorizer.authorize(event)

    # Then
    assert result == AuthorizationResult.FAIL
    assert response.status_code == 401
