from eternal_guesses import handler
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.repositories.configs_repository import ConfigsRepositoryImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from tests.integration.helpers import create_context, make_discord_create_event, \
    make_discord_guess_event, make_discord_manage_post_event, make_discord_change_guess_event, \
    make_discord_delete_guess_event


def test_integration_full_flow():
    # Given
    guild_id = 1
    games_repository = GamesRepositoryImpl()

    management_channel = 500
    guild_config = GuildConfig(guild_id=guild_id, management_channels=[management_channel])
    configs_repository = ConfigsRepositoryImpl()
    configs_repository.save(guild_config)

    # We start without games
    all_games = games_repository.get_all(guild_id)
    assert len(all_games) == 0

    # Create a new game
    game_id = 'game-1'
    game_title = 'Testing Game'
    game_description = 'This game is merely for show!'
    create_new_game(guild_id=guild_id,
                    game_id=game_id,
                    title=game_title,
                    description=game_description,
                    channel_id=management_channel)

    game = games_repository.get(guild_id, game_id)
    assert game.guild_id == guild_id
    assert game.game_id == game_id
    assert game.title == game_title
    assert game.description == game_description

    # Vote on the game
    user_id = 100
    guess = "500"
    guess_on_game(guild_id=guild_id, game_id=game_id, guess=guess, user_id=user_id)

    game = games_repository.get(guild_id, game_id)
    assert user_id in game.guesses
    assert game.guesses[user_id].guess == guess

    # Post a channel message
    post_channel_message(guild_id=guild_id, game_id=game_id, channel_id=management_channel)

    # Vote twice more as the same user
    another_user_id = 101
    guess = "500"
    guess_on_game(guild_id=guild_id, game_id=game_id, guess=guess, user_id=another_user_id)
    guess_on_game(guild_id=guild_id, game_id=game_id, guess=guess, user_id=another_user_id)

    game = games_repository.get(guild_id, game_id)
    assert another_user_id in game.guesses
    assert game.guesses[another_user_id].guess == guess
    assert len(game.guesses) == 2

    # Change a member's guess as a management user
    new_guess = "5600"
    change_guess(guild_id=guild_id, game_id=game_id, guessing_user_id=user_id, new_guess=new_guess,
                 channel_id=management_channel)

    game = games_repository.get(guild_id, game_id)
    assert game.guesses[user_id].guess == new_guess

    # Delete a member's guess as a management user
    delete_guess(guild_id=guild_id, game_id=game_id, guessing_user_id=user_id, channel_id=management_channel)

    game = games_repository.get(guild_id, game_id)
    assert user_id not in game.guesses
    assert another_user_id in game.guesses


def guess_on_game(guild_id: int, game_id: str, guess: str, user_id: int):
    response = handler.handle_lambda(
        make_discord_guess_event(guild_id=guild_id, game_id=game_id, guess=guess, user_id=user_id),
        create_context()
    )

    assert response['statusCode'] == 200


def create_new_game(guild_id: int, game_id: str, title: str, description: str, channel_id: int):
    response = handler.handle_lambda(
        make_discord_create_event(
            guild_id=guild_id,
            game_id=game_id,
            game_title=title,
            game_description=description,
            channel_id=channel_id,
        ),
        create_context()
    )

    assert response['statusCode'] == 200


def post_channel_message(guild_id: int, game_id: str, channel_id: int):
    response = handler.handle_lambda(
        make_discord_manage_post_event(
            guild_id=guild_id,
            game_id=game_id,
            channel_id=channel_id),
        create_context()
    )

    assert response['statusCode'] == 200


def change_guess(guild_id: int, game_id: str, new_guess: str, guessing_user_id: int, channel_id: int):
    response = handler.handle_lambda(
        make_discord_change_guess_event(
            guild_id=guild_id, game_id=game_id, member=guessing_user_id, new_guess=new_guess, channel_id=channel_id
        ),
        create_context()
    )

    assert response['statusCode'] == 200


def delete_guess(guild_id: int, game_id: str, guessing_user_id: int, channel_id: int):
    response = handler.handle_lambda(
        make_discord_delete_guess_event(
            guild_id=guild_id, game_id=game_id, member=guessing_user_id, channel_id=channel_id
        ),
        create_context()
    )

    assert response['statusCode'] == 200
