import re
from datetime import datetime

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds
from eternal_guesses.util.game_post_manager import GamePostManager
from eternal_guesses.util.message_provider import MessageProvider


class SubmitGuessRoute(Route):
    def __init__(
        self,
        games_repository: GamesRepository,
        message_provider: MessageProvider,
        game_post_manager: GamePostManager
    ):
        self.games_repository = games_repository
        self.message_provider = message_provider
        self.game_post_manager = game_post_manager

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        user_id = event.member.user_id
        user_nickname = event.member.nickname

        modal_id = event.modal_submit.modal_custom_id
        game_id = re.search(
            ComponentIds.submit_guess_modal_regex,
            modal_id
        ).group(1)
        guess = event.modal_submit.inputs[ComponentIds.submit_guess_input_value]

        game = self.games_repository.get(guild_id, game_id)
        if game is None:
            error_message = self.message_provider.error_game_not_found(game_id)
            return DiscordResponse.ephemeral_channel_message(
                content=error_message
            )

        if game.guesses.get(user_id) is not None:
            error_message = self.message_provider.error_duplicate_guess(game_id)
            return DiscordResponse.ephemeral_channel_message(error_message)

        if game.closed:
            error_message = self.message_provider.error_guess_on_closed_game(
                game_id
            )
            return DiscordResponse.ephemeral_channel_message(error_message)

        if game.is_numeric():
            if not self.validate_guess(game=game, guess=guess):
                error_message = self.message_provider.invalid_guess(game)
                return DiscordResponse.ephemeral_channel_message(error_message)

        game_guess = GameGuess()
        game_guess.user_id = user_id
        game_guess.user_nickname = user_nickname
        game_guess.timestamp = datetime.now()
        game_guess.guess = guess

        game.guesses[int(user_id)] = game_guess
        self.games_repository.save(game)

        await self.game_post_manager.update(game)

        guess_added_message = self.message_provider.guess_added(game_id, guess)
        return DiscordResponse.ephemeral_channel_message(
            content=guess_added_message
        )

    def validate_guess(self, game: Game, guess: str):
        if not self.is_numeric(guess):
            return False

        if game.max_guess is not None and int(guess) > game.max_guess:
            return False

        if game.min_guess is not None and int(guess) < game.min_guess:
            return False

        return True

    def is_numeric(self, guess: str):
        try:
            int(guess)
            return True
        except ValueError:
            return False
