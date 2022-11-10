import json

from eternal_guesses import event_handler
from eternal_guesses.model.discord.discord_event import InteractionType


def test_ping():
    # Given
    event = {
        'body': json.dumps({
            "id": "00000001",
            "token": "some-token-abcde1234567890",
            "type": InteractionType.PING.value,
            "version": 1
        }),
        'headers': {},
    }

    # When
    response = event_handler.handle(event)

    # Then
    assert response['statusCode'] == 200
    assert response['headers']['Content-Type'] == 'application/json'
    assert json.loads(response['body']) == {'type': 1}
