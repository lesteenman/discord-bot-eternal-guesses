import logging
from datetime import datetime

from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository

log = logging.getLogger(__name__)


class GuessRoute:
    def __init__(self, games_repository: GamesRepository, discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider):
        self.games_repository = games_repository
        self.discord_messaging = discord_messaging
        self.message_provider = message_provider

    async def _update_channel_messages(self, game: Game):
        log.info(
            f"updating {len(game.channel_messages)} channel messages for {game.game_id}")
        if game.channel_messages is not None:
            new_channel_message = self.message_provider.channel_list_game_guesses(game)
            for channel_message in game.channel_messages:
                log.debug(f"sending update to channel message, channel_id={channel_message.channel_id}, "
                          f"message_id={channel_message.message_id}, message='{new_channel_message}'")
                await self.discord_messaging.update_channel_message(channel_message.channel_id,
                                                                    channel_message.message_id,
                                                                    new_channel_message)

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        user_id = event.member.user_id
        user_nickname = event.member.nickname
        game_id = event.command.options['game-id']
        guess = event.command.options['guess']

        game = self.games_repository.get(guild_id, game_id)
        if game is None:
            dm_error = self.message_provider.dm_error_game_not_found(game_id)
            await self.discord_messaging.send_dm(event.member, dm_error)

            return DiscordResponse.acknowledge()

        if game.guesses.get(user_id) is not None:
            dm_error = self.message_provider.dm_error_duplicate_guess(game_id)
            await self.discord_messaging.send_dm(event.member, dm_error)

            return DiscordResponse.acknowledge()

        if game.closed:
            dm_error = self.message_provider.dm_error_guess_on_closed_game(game_id)
            await self.discord_messaging.send_dm(event.member, dm_error)

            return DiscordResponse.acknowledge()

        game_guess = GameGuess()
        game_guess.user_id = user_id
        game_guess.user_nickname = user_nickname
        game_guess.timestamp = datetime.now()
        game_guess.guess = guess

        game.guesses[int(user_id)] = game_guess
        self.games_repository.save(game)

        guess_added_dm = self.message_provider.dm_guess_added(game_id, guess)
        await self.discord_messaging.send_dm(event.member, guess_added_dm)

        await self._update_channel_messages(game)

        return DiscordResponse.acknowledge()
