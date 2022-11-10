import pytest
from discord_interactions import InteractionType

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.routes.commands.ping import PingRoute

pytestmark = pytest.mark.asyncio


async def test_ping():
    # Given
    ping_route = PingRoute()

    # When
    response = await ping_route.call(DiscordEvent())

    # Then
    assert response.json() == {'type': InteractionType.PING}
