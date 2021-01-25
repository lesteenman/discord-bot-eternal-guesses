from discord_interactions import InteractionType
from eternal_guesses.routes import ping


def test_ping():
    # When
    response = ping.call()

    # Then
    assert response.json() == {'type': InteractionType.PING}
