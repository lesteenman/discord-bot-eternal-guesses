from eternal_guesses.exceptions import GuessNotFoundError, GameNotFoundError
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.util.game_post_manager import GamePostManager


class GuessesService:
    def __init__(
        self,
        games_repository: GamesRepository,
        game_post_manager: GamePostManager,
    ):
        self.game_post_manager = game_post_manager
        self.games_repository = games_repository

    async def edit(self, guild_id: int, game_id: str, member: int, guess: str):
        game = self.games_repository.get(guild_id=guild_id, game_id=game_id)

        if game is None:
            raise GameNotFoundError(f"could not foind game {game_id}")

        if member not in game.guesses:
            raise GuessNotFoundError(
                f"could not find {member} in guesses of game {game}"
            )

        game.guesses[member].guess = guess
        self.games_repository.save(game)

        await self.game_post_manager.update(game)

    async def delete(self, guild_id: int, game_id: str, member: int):
        game = self.games_repository.get(guild_id=guild_id, game_id=game_id)

        if game is None:
            raise GameNotFoundError()

        if member not in game.guesses:
            raise GuessNotFoundError()

        del game.guesses[member]

        self.games_repository.save(game)

        await self.game_post_manager.update(game)
