import json
from unittest.mock import patch

import router
from discord_interactions import InteractionType


@patch('routes.ping.call')
def test_handle_ping(mock_handler_ping):
    # Given
    expected_return_value = {'type': InteractionType.PING}
    mock_handler_ping.return_value = expected_return_value

    body = {
        'type': 1,
        'bogus': 'value',
    }

    # When
    response = router.route(body)

    # Then
    mock_handler_ping.assert_called_with(body)
    assert response.status_code == 200
    assert json.loads(response.body) == expected_return_value
