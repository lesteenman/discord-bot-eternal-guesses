import json

from eternal_guesses import handler


def test_handle_lambda(mocker):
    # Given
    ping_mock = mocker.patch(
        'handlers.ping.call',
        return_value={'type': 1}
    )

    body = {'type': 1}
    event = {
        'body': json.dumps(body),
    }
    context = {}

    # When
    response = handler.handle_lambda(event, context)

    # Then
    ping_mock.assert_called_with(body)
    assert json.loads(response['body']) == body
