import pytest
from discord_interactions import InteractionType
from eternal_guesses.routes import ping

pytestmark = pytest.mark.asyncio


async def test_ping():
    # When
    response = await ping.call()

    # Then
    assert response.json() == {'type': InteractionType.PING}
