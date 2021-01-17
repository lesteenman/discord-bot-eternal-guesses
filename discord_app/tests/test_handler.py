import json

from eternal_guesses import handler


def test_handle_lambda(mocker):
    # Given
    discord_router_mock = mocker.patch('eternal_guesses.discord_router.handle',
                                       return_value={'type': 1})

    body = {'type': 1}
    event = {
        'body': json.dumps(body),
        'path': 'discord/'
    }
    context = {}

    # When
    handler.handle_lambda(event, context)

    # Then
    discord_router_mock.assert_called_with(body)
