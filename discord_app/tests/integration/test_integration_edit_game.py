import json

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_response import ResponseType
from eternal_guesses.repositories.games_repository import GamesRepositoryImpl
from tests.integration.test_helpers import select_string, \
    has_selector_with_option, click_button_component, \
    submit_modal, is_modal_with_id, send_command, response_has_button, has_input


def test_integration_edit_game(eternal_guesses_table):
    # Preparation
    guild_id = 1
    games_repository = GamesRepositoryImpl(eternal_guesses_table)

    # Create a game to test with
    game_id = 'game-to-be-changed'
    games_repository.save(
        Game(
            guild_id=guild_id,
            game_id='game-to-be-changed',
            title='original title',
            description='description',
            min_guess=1,
            max_guess=10,
            created_by=-1,
        )
    )

    # Edit the title
    new_game_title = "New game title"
    edit_title(
        guild_id=guild_id,
        game_id=game_id,
        new_title=new_game_title,
    )

    game = games_repository.get(guild_id, game_id)
    assert game.title == new_game_title

    # Edit the description
    new_description = "New game description"
    edit_description(
        guild_id=guild_id,
        game_id=game_id,
        new_description=new_description,
    )

    game = games_repository.get(guild_id, game_id)
    assert game.description == new_description

    # Edit the min guess
    new_min_guess = "50"
    edit_min_guess(
        guild_id=guild_id,
        game_id=game_id,
        new_min_guess=new_min_guess,
    )

    game = games_repository.get(guild_id, game_id)
    assert game.min_guess == int(new_min_guess)

    # Edit the max guess
    new_max_guess = "246"
    edit_max_guess(
        guild_id=guild_id,
        game_id=game_id,
        new_max_guess=new_max_guess,
    )

    game = games_repository.get(guild_id, game_id)
    assert game.max_guess == int(new_max_guess)

    # Edit the min guess with a non-numeric value


def trigger_manage_game_post(game_id: str, guild_id: int, is_closed: bool):
    # List the games
    if is_closed:
        response = send_command(
            command_name="list-games",
            guild_id=guild_id,
            options={"include-closed": True}
        )
    else:
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
    return body


def edit_title(guild_id, game_id, new_title):
    button_id = ComponentIds.button_edit_game_title_id(game_id)
    modal_id = ComponentIds.edit_game_title_modal_id(game_id)
    input_id = ComponentIds.edit_game_title_input

    edit_game_field(
        guild_id=guild_id,
        game_id=game_id,
        button_id=button_id,
        modal_id=modal_id,
        modal_input_id=input_id,
        new_value=new_title
    )


def edit_description(guild_id, game_id, new_description):
    button_id = ComponentIds.button_edit_game_description_id(game_id)
    modal_id = ComponentIds.edit_game_description_modal_id(game_id)
    input_id = ComponentIds.edit_game_description_input

    edit_game_field(
        guild_id=guild_id,
        game_id=game_id,
        button_id=button_id,
        modal_id=modal_id,
        modal_input_id=input_id,
        new_value=new_description
    )


def edit_min_guess(guild_id, game_id, new_min_guess):
    button_id = ComponentIds.button_edit_game_min_guess_id(game_id)
    modal_id = ComponentIds.edit_game_min_guess_modal_id(game_id)
    modal_input_id = ComponentIds.edit_game_min_guess_input

    edit_game_field(
        guild_id,
        game_id,
        button_id,
        modal_id,
        modal_input_id,
        new_min_guess
    )


def edit_max_guess(guild_id, game_id, new_max_guess):
    button_id = ComponentIds.button_edit_game_max_guess_id(game_id)
    modal_id = ComponentIds.edit_game_max_guess_modal_id(game_id)
    modal_input_id = ComponentIds.edit_game_max_guess_input

    edit_game_field(
        guild_id,
        game_id,
        button_id,
        modal_id,
        modal_input_id,
        new_max_guess
    )


def edit_game_field(
    guild_id,
    game_id,
    button_id,
    modal_id,
    modal_input_id,
    new_value
):
    body = trigger_edit_game_post(game_id, guild_id)

    # Click 'edit min_guess'
    assert response_has_button(body, button_id)
    body = click_button_component(
        component_custom_id=button_id,
        guild_id=guild_id
    )
    # Submit the new min_guess
    assert is_modal_with_id(
        body,
        modal_id=modal_id
    )
    assert has_input(
        body,
        component_custom_id=modal_input_id
    )
    submit_modal(
        guild_id=guild_id,
        modal_id=modal_id,
        inputs={
            modal_input_id: new_value
        }
    )


def trigger_edit_game_post(game_id, guild_id):
    body = trigger_manage_game_post(
        guild_id=guild_id,
        game_id=game_id,
        is_closed=False,
    )
    assert response_has_button(
        body,
        ComponentIds.component_button_edit_game_id(game_id)
    )
    body = click_button_component(
        guild_id=guild_id,
        component_custom_id=ComponentIds.component_button_edit_game_id(game_id)
    )
    return body
