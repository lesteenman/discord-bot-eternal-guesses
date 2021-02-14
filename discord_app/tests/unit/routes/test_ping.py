import pytest
from discord_interactions import InteractionType
from eternal_guesses.routes import ping
from eternal_guesses.routes.ping import PingRoute

pytestmark = pytest.mark.asyncio


async def test_ping():
    # Given
    ping_route = PingRoute()

    # When
    response = await ping_route.call()

    # Then
    assert response.json() == {'type': InteractionType.PING}
