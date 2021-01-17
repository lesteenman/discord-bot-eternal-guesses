from eternal_guesses.views import ping


def test_ping():
    # Given
    body = {'type': 1}

    # When
    response = ping.call(body)

    # Then
    assert response == body
