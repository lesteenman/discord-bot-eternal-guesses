from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_component_action import \
    DiscordComponentAction
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.discord.discord_response import ResponseType
from eternal_guesses.routes.trigger_guess_modal import TriggerGuessModalRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_call_returns_modal_response():
    # Given
    event = DiscordEvent(
        member=DiscordMember(user_id=1),
        component_action=DiscordComponentAction(
            component_type=ComponentType.BUTTON,
            component_custom_id="button_trigger_guess_modal_my_testing_game_id"
        )
    )

    # Static messages
    modal_input_label = "Input label"
    modal_title = "Modal title"

    message_provider = MagicMock(MessageProvider)
    message_provider.modal_input_label_guess_value.return_value = modal_input_label
    message_provider.modal_title_place_guess.return_value = modal_title

    test_game = Game()
    games_repository = FakeGamesRepository([test_game])

    route = TriggerGuessModalRoute(
        message_provider=message_provider,
        games_repository=games_repository,
    )

    # When
    response = await route.call(event)

    # Then
    assert response.json() == {
        'type': ResponseType.MODAL.value,
        'data': {
            'custom_id': 'modal_submit_guess_my_testing_game_id',
            'title': modal_title,
            'components': [
                {
                    'type': 1,
                    'components': [
                        {
                            'type': 4,
                            'custom_id': 'modal_input_guess_value_my_testing_game_id',
                            'label': modal_input_label,
                            'style': 1,
                        }
                    ]
                }
            ]
        }
    }
