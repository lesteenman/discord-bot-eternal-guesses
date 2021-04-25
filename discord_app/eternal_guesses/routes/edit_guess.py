from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.game_post_manager import GamePostManager
from eternal_guesses.util.message_provider import MessageProvider


class EditGuessRoute(Route):
    def __init__(self,
                 games_repository: GamesRepository,
                 message_provider: MessageProvider,
                 game_post_manager: GamePostManager):
        self.games_repository = games_repository
        self.message_provider = message_provider
        self.game_post_manager = game_post_manager

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = event.command.options['game-id']
        member = int(event.command.options['member'])
        guess = event.command.options['guess']

        game = self.games_repository.get(guild_id=guild_id, game_id=game_id)

        if game is None:
            game_not_found_error = self.message_provider.error_game_not_found(game_id)
            return DiscordResponse.ephemeral_channel_message(game_not_found_error)

        if member not in game.guesses:
            guess_not_found_error = self.message_provider.error_guess_not_found(game_id, member)
            return DiscordResponse.ephemeral_channel_message(guess_not_found_error)

        game.guesses[member].guess = guess
        self.games_repository.save(game)

        await self.game_post_manager.update(game)

        guess_edited_message = self.message_provider.guess_edited()
        return DiscordResponse.ephemeral_channel_message(guess_edited_message)
