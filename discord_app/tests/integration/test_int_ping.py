import json

from discord_interactions import InteractionType

from eternal_guesses.api import handler


def test_ping():
    # Given
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
