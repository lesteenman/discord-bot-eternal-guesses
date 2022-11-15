import json

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_response import ResponseType
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from tests.integration.test_helpers import is_ephemeral_channel_message, \
    select_string, has_selector_with_option, click_button_component, \
    submit_modal, is_modal_with_id, send_command, response_has_button, select_channel, \
    has_channel_selector, trigger_manage_game_post


def test_integration_full_flow(eternal_guesses_table):
    # Given
    guild_id = 1
    games_repository = GamesRepositoryImpl(eternal_guesses_table)

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
        channel_id=500
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
    post_channel_id = 5342
    post_channel_message(
        guild_id=guild_id,
        game_id=game_id,
        target_channel=post_channel_id,
    )
    game = games_repository.get(guild_id, game_id)
    assert any([m.channel_id == post_channel_id for m in game.channel_messages])

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

    # Change a member's guess
    new_guess = "4900"
    change_guess(
        guild_id=guild_id,
        game_id=game_id,
        guessing_user_id=user_id,
        new_guess=new_guess,
    )

    game = games_repository.get(guild_id, game_id)
    assert game.guesses[user_id].guess == new_guess

    # Delete a member's guess
    delete_guess(
        guild_id=guild_id,
        game_id=game_id,
        guessing_user_id=user_id,
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

    # Close the game
    close_game(
        guild_id=guild_id,
        game_id=game_id,
    )
    game = games_repository.get(guild_id, game_id)
    assert game.closed

    # Reopen the game
    reopen_game(
        guild_id=guild_id,
        game_id=game_id,
    )
    game = games_repository.get(guild_id, game_id)
    assert not game.closed


def guess_on_game(guild_id: int, game_id: str, guess: str, user_id: int):
    click_guess_button(guild_id=guild_id, game_id=game_id, user_id=user_id)
    submit_guess_modal(
        guild_id=guild_id,
        user_id=user_id,
        game_id=game_id,
        guess=guess
    )


def click_guess_button(guild_id: int, game_id: str, user_id: int):
    body = click_button_component(
        component_custom_id=ComponentIds.component_button_guess_id(game_id),
        guild_id=guild_id,
        user_id=user_id
    )

    assert body['type'] in [ResponseType.MODAL.value,
                            ResponseType.CHANNEL_MESSAGE.value]
    if body['type'] == ResponseType.MODAL.value:
        assert game_id in body['data']['title']
        assert body['data']['custom_id'].endswith(game_id)


def submit_guess_modal(guild_id: int, game_id: str, user_id: int, guess: str):
    submit_modal(
        guild_id=guild_id,
        inputs={
            ComponentIds.submit_guess_input_value: guess
        },
        modal_id=ComponentIds.submit_guess_modal_id(game_id),
        user_id=user_id
    )


def create_new_game(
    guild_id: int, game_id: str, title: str, description: str, channel_id: int,
    min_guess: int, max_guess: int
):
    response = send_command(
        guild_id=guild_id,
        command_name="create-game",
    )

    body = json.loads(response['body'])
    assert body['type'] == ResponseType.MODAL.value

    submit_modal(
        guild_id=guild_id,
        modal_id=ComponentIds.submit_create_modal_id,
        inputs={
            ComponentIds.submit_create_input_game_id: game_id,
            ComponentIds.submit_create_input_title: title,
            ComponentIds.submit_create_input_description: description,
            ComponentIds.submit_create_input_min_value: min_guess,
            ComponentIds.submit_create_input_max_value: max_guess,
        }
    )


def post_channel_message(
    guild_id: int,
    game_id: str,
    target_channel: int
):
    # Trigger the 'manage game' post
    body = trigger_manage_game_post(
        game_id=game_id,
        guild_id=guild_id,
        is_closed=False,
    )

    # Verify the message has a 'post' button
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value
    assert response_has_button(
        body,
        component_custom_id=ComponentIds.component_button_post_game_id(game_id),
    )

    # Click the 'post' button on the 'manage game' post
    body = click_button_component(
        component_custom_id=ComponentIds.component_button_post_game_id(game_id),
        guild_id=guild_id,
    )

    # Select the channel to post to
    assert has_channel_selector(
        body,
        ComponentIds.selector_post_game_id(game_id),
    )
    select_channel(
        guild_id=guild_id,
        component_custom_id=ComponentIds.selector_post_game_id(game_id),
        values=[target_channel],
    )


def close_game(guild_id, game_id):
    # Trigger the 'manage game' post
    body = trigger_manage_game_post(
        game_id=game_id,
        guild_id=guild_id,
        is_closed=False,
    )

    # Verify the 'close' button is on the post
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value
    assert response_has_button(
        body,
        component_custom_id=ComponentIds.component_button_close_game_id(
            game_id=game_id
        ),
    )

    # Click the 'close' button on the 'manage game' post
    click_button_component(
        component_custom_id=ComponentIds.component_button_close_game_id(
            game_id=game_id,
        ),
        guild_id=guild_id,
    )


def reopen_game(guild_id, game_id):
    body = trigger_manage_game_post(
        game_id=game_id,
        guild_id=guild_id,
        is_closed=True,
    )

    # Verify the 'reopen' button is on the post
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value
    assert response_has_button(
        body,
        component_custom_id=ComponentIds.component_button_reopen_game_id(
            game_id=game_id
        ),
    )

    # Click the 'reopen' button on the 'manage game' post
    click_button_component(
        component_custom_id=ComponentIds.component_button_reopen_game_id(
            game_id=game_id,
        ),
        guild_id=guild_id,
    )


def change_guess(
    guild_id: int,
    game_id: str,
    new_guess: str,
    guessing_user_id: int,
):
    # Trigger the 'manage game' post
    trigger_manage_game_post(
        game_id=game_id,
        guild_id=guild_id,
        is_closed=False,
    )

    # Click the 'edit guess' button on the 'manage game' post
    body = click_button_component(
        component_custom_id=ComponentIds.component_button_edit_guess_id(
            game_id
        ),
        guild_id=guild_id,
    )

    # Verify our old guess is in the list
    assert has_selector_with_option(
        body,
        ComponentIds.component_select_edit_guess_id(game_id),
        guessing_user_id
    )

    # Select the old guess, triggering the 'change guess' modal
    select_body = select_string(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_select_edit_guess_id(
            game_id
        ),
        values=[guessing_user_id]
    )
    assert is_modal_with_id(
        select_body,
        ComponentIds.edit_guess_modal_id(
            game_id=game_id,
            member_id=guessing_user_id
        )
    )

    # Submit the new guess in the given modal
    body = submit_modal(
        guild_id=guild_id,
        modal_id=ComponentIds.edit_guess_modal_id(
            game_id=game_id,
            member_id=guessing_user_id
        ),
        inputs={
            ComponentIds.edit_guess_modal_input_id: new_guess
        }
    )

    assert is_ephemeral_channel_message(body)


def delete_guess(
    guild_id: int,
    game_id: str,
    guessing_user_id: int,
):
    # Trigger the 'manage game' post
    trigger_manage_game_post(
        game_id=game_id,
        guild_id=guild_id,
        is_closed=False,
    )

    # Click the 'delete guess' button on the 'manage game' post
    body = click_button_component(
        component_custom_id=ComponentIds.component_button_delete_guess_id(
            game_id
        ),
        guild_id=guild_id,
    )

    # Verify our guess is in the list
    assert has_selector_with_option(
        body,
        ComponentIds.component_select_delete_guess_id(game_id),
        guessing_user_id
    )

    # Select the guess
    select_body = select_string(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_select_delete_guess_id(
            game_id
        ),
        values=[guessing_user_id]
    )
    assert is_ephemeral_channel_message(select_body)
