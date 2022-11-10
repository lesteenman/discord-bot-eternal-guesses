import json

from eternal_guesses import event_handler
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_response import ResponseType
from eternal_guesses.repositories.configs_repository import \
    ConfigsRepositoryImpl
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from eternal_guesses.util.component_ids import ComponentIds
from tests.integration import discord_events


def test_integration_full_flow(eternal_guesses_table):
    # Given
    guild_id = 1
    games_repository = GamesRepositoryImpl(eternal_guesses_table)

    management_channel = 500
    guild_config = GuildConfig(
        guild_id=guild_id,
        management_channels=[management_channel]
    )
    configs_repository = ConfigsRepositoryImpl(eternal_guesses_table)
    configs_repository.save(guild_config)

    # We start without games
    all_games = games_repository.get_all(guild_id)
    assert len(all_games) == 0

    # Create a new game
    game_id = 'game-1'
    game_title = 'Testing Game'
    game_description = 'This game is merely for show!'
    create_new_game(
        guild_id=guild_id,
        game_id=game_id,
        title=game_title,
        description=game_description,
        min_guess=50,
        max_guess=5000,
        channel_id=management_channel
    )

    game = games_repository.get(guild_id, game_id)
    assert game.guild_id == guild_id
    assert game.game_id == game_id
    assert game.title == game_title
    assert game.description == game_description

    # Vote on the game
    user_id = 100
    guess = "500"
    guess_on_game(
        guild_id=guild_id,
        game_id=game_id,
        user_id=user_id,
        guess=guess
    )

    game = games_repository.get(guild_id, game_id)
    assert user_id in game.guesses
    assert game.guesses[user_id].guess == guess

    # Post a channel message
    post_channel_message(
        guild_id=guild_id,
        game_id=game_id,
        channel_id=management_channel
    )

    # Vote twice more as the same user
    another_user_id = 101
    guess = "500"
    guess_on_game(
        guild_id=guild_id,
        game_id=game_id,
        guess=guess,
        user_id=another_user_id
    )
    guess_on_game(
        guild_id=guild_id,
        game_id=game_id,
        guess=guess,
        user_id=another_user_id
    )

    game = games_repository.get(guild_id, game_id)
    assert another_user_id in game.guesses
    assert game.guesses[another_user_id].guess == guess
    assert len(game.guesses) == 2

    # Change a member's guess as a management user
    new_guess = "4900"
    change_guess(
        guild_id=guild_id,
        game_id=game_id,
        guessing_user_id=user_id,
        new_guess=new_guess,
        channel_id=management_channel
    )

    game = games_repository.get(guild_id, game_id)
    assert game.guesses[user_id].guess == new_guess

    # Delete a member's guess as a management user
    delete_guess(
        guild_id=guild_id,
        game_id=game_id,
        guessing_user_id=user_id,
        channel_id=management_channel
    )

    game = games_repository.get(guild_id, game_id)
    assert user_id not in game.guesses
    assert another_user_id in game.guesses

    # Place a guess that's below the min
    one_more_user_id = 102
    guess_on_game(
        guild_id=guild_id,
        game_id=game_id,
        guess="49",
        user_id=one_more_user_id
    )

    game = games_repository.get(guild_id, game_id)
    assert one_more_user_id not in game.guesses

    # Place a guess that's above the max
    guess_on_game(
        guild_id=guild_id,
        game_id=game_id,
        guess="5001",
        user_id=one_more_user_id
    )

    game = games_repository.get(guild_id, game_id)
    assert one_more_user_id not in game.guesses


def guess_on_game(guild_id: int, game_id: str, guess: str, user_id: int):
    click_guess_button(guild_id=guild_id, game_id=game_id, user_id=user_id)
    submit_guess_modal(
        guild_id=guild_id,
        user_id=user_id,
        game_id=game_id,
        guess=guess
    )


def click_guess_button(guild_id: int, game_id: str, user_id: int):
    event = discord_events.component_action(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_button_guess_id(game_id),
        component_type=ComponentType.BUTTON,
        user_id=user_id,
    )
    response = event_handler.handle(event)

    assert response['statusCode'] == 200

    body = json.loads(response['body'])
    assert body['type'] in [ResponseType.MODAL.value,
                            ResponseType.CHANNEL_MESSAGE.value]
    if body['type'] == ResponseType.MODAL.value:
        assert game_id in body['data']['title']
        assert body['data']['custom_id'].endswith(game_id)


def submit_guess_modal(guild_id: int, game_id: str, user_id: int, guess: str):
    response = event_handler.handle(
        discord_events.modal_submit_event(
            guild_id=guild_id,
            user_id=user_id,
            modal_custom_id=ComponentIds.submit_guess_modal_id(game_id),
            inputs={
                ComponentIds.submit_guess_input_value: guess
            },
        ),
    )

    assert response['statusCode'] == 200


def create_new_game(
    guild_id: int, game_id: str, title: str, description: str, channel_id: int,
    min_guess: int, max_guess: int
):
    trigger_modal_event = discord_events.application_command(
        command_name="create-game",
        guild_id=guild_id,
        channel_id=channel_id,
    )

    response = event_handler.handle(trigger_modal_event)
    assert response['statusCode'] == 200

    body = json.loads(response['body'])
    assert body['type'] == ResponseType.MODAL.value

    submit_modal_event = discord_events.modal_submit_event(
        guild_id=guild_id,
        channel_id=channel_id,
        modal_custom_id=ComponentIds.submit_create_modal_id,
        inputs={
            ComponentIds.submit_create_input_game_id: game_id,
            ComponentIds.submit_create_input_title: title,
            ComponentIds.submit_create_input_description: description,
            ComponentIds.submit_create_input_min_value: min_guess,
            ComponentIds.submit_create_input_max_value: max_guess,
        }
    )

    response = event_handler.handle(submit_modal_event)
    assert response['statusCode'] == 200


def post_channel_message(guild_id: int, game_id: str, channel_id: int):
    response = event_handler.handle(
        discord_events.make_discord_manage_post_event(
            guild_id=guild_id,
            game_id=game_id,
            channel_id=channel_id
        ),
    )

    assert response['statusCode'] == 200


def change_guess(
    guild_id: int,
    game_id: str,
    new_guess: str,
    guessing_user_id: int,
    channel_id: int
):
    response = event_handler.handle(
        discord_events.make_discord_change_guess_event(
            guild_id=guild_id,
            game_id=game_id,
            member=guessing_user_id,
            new_guess=new_guess,
            channel_id=channel_id
        ),
    )

    assert response['statusCode'] == 200


def delete_guess(
    guild_id: int,
    game_id: str,
    guessing_user_id: int,
    channel_id: int
):
    response = event_handler.handle(
        discord_events.make_discord_delete_guess_event(
            guild_id=guild_id,
            game_id=game_id,
            member=guessing_user_id,
            channel_id=channel_id
        ),
    )

    assert response['statusCode'] == 200
