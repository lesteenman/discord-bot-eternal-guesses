from eternal_guesses import discord_messaging
from eternal_guesses import message_formatter
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository


async def post(event: DiscordEvent) -> DiscordResponse:
    guild_id = event.guild_id
    channel_id = event.command.options['channel']
    game_id = event.command.options['game-id']

    game = GamesRepository.get(guild_id, game_id)
    if game is None:
        message = message_formatter.dm_error_game_not_found(game_id)
        await discord_messaging.send_dm(event.member, message)
    else:
        message = message_formatter.channel_list_game_guesses(game)
        channel_message_id = await discord_messaging.create_channel_message(channel_id, message)

        if game.channel_messages is None:
            game.channel_messages = []

        game.channel_messages.append(channel_message_id)
        GamesRepository.save(guild_id, game)

    return DiscordResponse.acknowledge()


async def close(event: DiscordEvent) -> DiscordResponse:
    pass
