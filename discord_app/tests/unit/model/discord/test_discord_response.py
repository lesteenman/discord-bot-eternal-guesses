from eternal_guesses.model.discord.discord_response import DiscordResponse


def test_ephemeral_message():
    # Given
    discord_response = DiscordResponse.channel_message()

    # When
    discord_response.is_ephemeral = True

    # Then
    assert discord_response.flags & 64 == 64
    assert discord_response.is_ephemeral

    # When
    discord_response.is_ephemeral = False

    # Then
    assert discord_response.flags & 64 == 0
    assert not discord_response.is_ephemeral
