from eternal_guesses import discord_router


def test_route_ping(mocker):
    # Given
    ping_mock = mocker.patch(
        'eternal_guesses.views.ping.call',
        return_value={'type': 1}
    )
    body = {'type': 1}

    # When
    discord_router.handle(body)

    # Then
    ping_mock.assert_called_with(body)
