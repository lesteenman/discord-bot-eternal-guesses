from discord_interactions import InteractionType
from eternal_guesses.routes import ping


def test_ping():
    # Given
    body = {
        'type': 1,
        'bogus': 'value',
    }

    # When
    response = ping.call(body)

    # Then
    assert response == {'type': InteractionType.PING}
