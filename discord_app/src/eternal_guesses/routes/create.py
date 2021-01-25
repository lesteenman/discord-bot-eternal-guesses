from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories import games_repository
from eternal_guesses.util import id_generator


def generate_game_id(attempt: int = 0):
    if attempt >= 10:
        raise Exception(f"Could not generate a unique game_id after {attempt} attempts.")

    game_id = id_generator.game_id()
    existing_game = games_repository.get(game_id)
    print(f"existing game for game_id {game_id} = {existing_game}")
    if existing_game is None:
        return game_id
    else:
        return generate_game_id(attempt + 1)


def call(event: DiscordEvent) -> DiscordResponse:
    game_id = event.command.options.get('game-id')
    if game_id is None:
        game_id = generate_game_id()
    else:
        existing_game = games_repository.get(game_id)
        if existing_game is not None:
            return DiscordResponse.channel_message_with_source(f"Game id '{game_id}' already exists.")

    game = Game()
    game.game_id = game_id
    games_repository.insert(game)

    return DiscordResponse.channel_message(f"Game created with id '{game_id}'.")


