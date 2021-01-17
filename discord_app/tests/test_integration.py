import json

from eternal_guesses import handler


def test_ping():
    # Given
    body = {
        'type': 1
    }
    event = {
        'body': json.dumps(body),
        'path': '/'
    }

    context = {}

    # When
    response = handler.handle_lambda(event, context)

    # Then
    assert response == body
