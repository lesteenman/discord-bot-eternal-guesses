from flask import Flask


def test_discord_callback(client: Flask, mocker):
    # Given
    discord_router_mock = mocker.patch(
        'eternal_guesses.discord_router.handle',
        return_value={}
    )

    # When
    body = {'type': 1}
    response = client.post("/", json=body)

    # Then
    assert response.status_code == 200
    discord_router_mock.assert_called_with(body)
