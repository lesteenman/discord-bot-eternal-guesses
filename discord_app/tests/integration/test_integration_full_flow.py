import json

from eternal_guesses import event_handler
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_response import ResponseType
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from eternal_guesses.util.component_ids import ComponentIds
from tests.integration import discord_events


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
    # TODO

    # Try to vote again
    # TODO

    # Reopen the game
    # TODO

    # Vote as another user after reopening
    # TODO


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


def post_channel_message(
    guild_id: int,
    game_id: str,
    target_channel: int
):
    # Trigger the 'manage game' post
    trigger_manage_game_post(game_id, guild_id)

    # Click the 'post' button on the 'manage game' post
    body = click_button_component(
        component_custom_id=ComponentIds.component_button_post_game_id(game_id),
        guild_id=guild_id,
    )

    # Select the channel to post to
    assert has_channel_selector(
        body,
        ComponentIds.component_select_post_game_id(game_id),
    )
    select_channel(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_select_post_game_id(game_id),
        values=[target_channel],
    )


def trigger_manage_game_post(game_id, guild_id):
    # List the games
    response = send_command(
        command_name="list-games",
        guild_id=guild_id
    )
    body = json.loads(response['body'])
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value

    # Verify the game is one of the options
    assert has_selector_with_option(
        body=body,
        component_custom_id=ComponentIds.component_select_game_to_manage,
        value=game_id
    )

    # Select the game to manage
    body = select_string(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_select_game_to_manage,
        values=[game_id],
    )
    assert body['type'] == ResponseType.CHANNEL_MESSAGE.value
    assert response_has_button(
        body,
        component_custom_id=ComponentIds.component_button_post_game_id(game_id),
    )


def change_guess(
    guild_id: int,
    game_id: str,
    new_guess: str,
    guessing_user_id: int,
):
    # Trigger the 'manage game' post
    trigger_manage_game_post(game_id, guild_id)

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
    assert is_modal(
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
    trigger_manage_game_post(game_id, guild_id)

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


def send_command(command_name, guild_id):
    response = event_handler.handle(
        discord_events.application_command(
            guild_id=guild_id,
            command_name=command_name,
        )
    )
    assert response['statusCode'] == 200
    return response


def select_string(guild_id, component_custom_id, values):
    response = event_handler.handle(
        discord_events.component_action(
            guild_id=guild_id,
            component_custom_id=component_custom_id,
            component_type=ComponentType.STRING_SELECT,
            values=values,
        )
    )
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def select_channel(guild_id, component_custom_id, values):
    response = event_handler.handle(
        discord_events.component_action(
            guild_id=guild_id,
            component_custom_id=component_custom_id,
            component_type=ComponentType.CHANNEL_SELECT,
            values=values,
        )
    )
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def click_button_component(
    component_custom_id,
    guild_id,
    user_id=discord_events.DEFAULT_USER_ID
):
    event = discord_events.component_action(
        guild_id=guild_id,
        component_custom_id=component_custom_id,
        component_type=ComponentType.BUTTON,
        user_id=user_id,
    )
    response = event_handler.handle(event)
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def submit_modal(
    guild_id,
    modal_id,
    inputs,
    user_id=discord_events.DEFAULT_USER_ID
):
    response = event_handler.handle(
        discord_events.modal_submit_event(
            guild_id=guild_id,
            user_id=user_id,
            modal_custom_id=modal_id,
            inputs=inputs,
        ),
    )
    assert response['statusCode'] == 200
    return json.loads(response['body'])


def is_modal(body, modal_id):
    if body['type'] != ResponseType.MODAL.value:
        return False

    return body['data']['custom_id'] == modal_id


def is_ephemeral_channel_message(body):
    # https://discord.com/developers/docs/resources/channel#message-object-message-flags
    return (
        body['type'] == ResponseType.CHANNEL_MESSAGE.value and
        body['data']['flags'] & (1 << 6)
    )


def has_selector_with_option(body, component_custom_id, value):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.STRING_SELECT.value and
                component['custom_id'] == component_custom_id and
                any([value == o['value'] for o in component['options']])
            ):
                return True

    return False


def has_channel_selector(body: dict, component_custom_id: str):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.CHANNEL_SELECT.value and
                component['custom_id'] == component_custom_id
            ):
                return True

    return False


def response_has_button(body, component_custom_id):
    for action_bar in body['data']['components']:
        for component in action_bar['components']:
            if (
                component['type'] == ComponentType.BUTTON.value and
                component['custom_id'] == component_custom_id
            ):
                return True

    assert False
