from eternal_guesses import discord_messaging, message_formatter
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository as games_repository
from model.data.game import Game


async def update_channel_messages(game: Game):
    if game.channel_messages is not None:
        new_channel_message = message_formatter.channel_list_game_guesses(game)
        for channel_message_id in game.channel_messages:
            await discord_messaging.update_channel_message(channel_message_id, new_channel_message)


async def call(event: DiscordEvent) -> DiscordResponse:
    guild_id = event.guild_id
    user_id = event.member.user_id
    game_id = event.command.options['game-id']
    guess = event.command.options['guess']

    game = games_repository.get(guild_id, game_id)
    if game is None:
        dm_error = message_formatter.dm_error_game_not_found(game_id)
        await discord_messaging.send_dm(event.member, dm_error)

        return DiscordResponse.acknowledge()

    if game.guesses.get(user_id) is not None:
        await discord_messaging.send_dm(event.member, f"You already placed a guess for game '{game_id}', your guess was not registered.")

        return DiscordResponse.acknowledge()

    game.guesses[user_id] = guess
    games_repository.save(guild_id, game)

    guess_added_dm = message_formatter.dm_guess_added(game_id, guess)
    await discord_messaging.send_dm(event.member, guess_added_dm)

    await update_channel_messages(game)

    return DiscordResponse.acknowledge()
