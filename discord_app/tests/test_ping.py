from eternal_guesses.handlers import ping


def test_ping():
    # Given
    body = {'type': 1}

    # When
    response = ping.call(body)

    # Then
    assert response == body
