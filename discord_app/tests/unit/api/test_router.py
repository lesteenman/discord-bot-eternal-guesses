import json
import pprint

import pytest

from eternal_guesses.api.router import RouterImpl
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_component_action import \
    DiscordComponentAction
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse, \
    ResponseType
from eternal_guesses.routes.route import Route

pytestmark = pytest.mark.asyncio


async def test_handle_matching_action():
    # Given
    event = DiscordEvent(
        component_action=DiscordComponentAction(
            component_type=ComponentType.BUTTON,
            component_custom_id="button_trigger_test"
        )
    )

    expected_content = "Component action well handled."

    class TestRoute(Route):
        async def call(self, event: DiscordEvent) -> DiscordResponse:
            return DiscordResponse.ephemeral_channel_message(
                expected_content
            )

        @staticmethod
        def matches(event: DiscordEvent) -> bool:
            action = event.component_action
            if action is None:
                return False

            return (
                action.component_type == ComponentType.BUTTON and
                action.component_custom_id == "button_trigger_test"
            )

    router = RouterImpl(
        routes=[TestRoute()],
    )

    # When
    response = await router.route(event)

    # Then
    assert response.status_code == 200

    body = json.loads(response.body)
    pprint.pp(body)
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value
    assert body['data']['content'] == expected_content
