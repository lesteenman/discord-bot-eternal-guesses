import json
from unittest.mock import patch

from discord_interactions import InteractionType

from eternal_guesses import handler
from eternal_guesses.api_authorizer import AuthorizationResult


@patch.object(handler.api_authorizer, 'authorize', autospec=True)
def test_ping(mock_authorize):
    # Given
    mock_authorize.return_value = (AuthorizationResult.PASS, None)

    event = {
        'body': json.dumps({
            "id": "00000001",
            "token": "some-token-abcde1234567890",
            "type": InteractionType.PING,
            "version": 1
        }),
        'headers': {},
    }

    # When
    response = handler.handle_lambda(event, {})

    # Then
    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'application/json'
    assert json.loads(response['body']) == {'type': 1}
