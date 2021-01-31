from eternal_guesses import discord_messaging
from eternal_guesses import message_formatter
from eternal_guesses.model.data.game import ChannelMessage
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository


async def post(event: DiscordEvent) -> DiscordResponse:
    guild_id = event.guild_id
    game_id = event.command.options['game-id']

    if 'channel' in event.command.options:
        channel_id = event.command.options['channel']
    else:
        channel_id = event.channel_id

    game = GamesRepository.get(guild_id, game_id)
    if game is None:
        message = message_formatter.dm_error_game_not_found(game_id)
        await discord_messaging.send_dm(event.member, message)
    else:
        message = message_formatter.channel_list_game_guesses(game)
        message_id = await discord_messaging.create_channel_message(channel_id, message)

        if game.channel_messages is None:
            game.channel_messages = []

        game.channel_messages.append(ChannelMessage(channel_id, message_id))
        GamesRepository.save(guild_id, game)

    return DiscordResponse.acknowledge()


async def close(event: DiscordEvent) -> DiscordResponse:
    pass


async def list_games(event: DiscordEvent) -> DiscordResponse:
    guild_id = event.guild_id

    all_games = GamesRepository.get_all(guild_id)

    if 'closed' in event.command.options:
        if event.command.options['closed']:
            closed_games = list(filter(lambda g: g.closed, all_games))
            message = message_formatter.channel_manage_list_closed_games(
                closed_games)
        else:
            open_games = list(filter(lambda g: not g.closed, all_games))
            message = message_formatter.channel_manage_list_open_games(
                open_games)
    else:
        message = message_formatter.channel_manage_list_all_games(all_games)

    return DiscordResponse.channel_message(message)
