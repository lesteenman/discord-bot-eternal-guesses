from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.discord.discord_modal_submit import \
    DiscordModalSubmit
from eternal_guesses.repositories.games_repository import GamesRepository, \
    GamesRepositoryImpl
from eternal_guesses.routes.modal_submits import submit_create
from eternal_guesses.routes.modal_submits.submit_create import SubmitCreateRoute
from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.app.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio

GAME_CREATED_MESSAGE = "Game created."
DUPLICATE_GAME_ID = "Duplicate game id."


@patch.object(submit_create, 'datetime', autospec=True)
async def test_create_only_id(mock_datetime):
    # Given
    guild_id = 1002
    game_id = 'prolific-platypus'

    create_datetime = datetime.now()
    mock_datetime.now.return_value = create_datetime

    # And: a games repository without any games
    games_repository = FakeGamesRepository()

    create_route = _route(games_repository=games_repository)

    # When
    event = _make_event(
        game_id=game_id,
        guild_id=guild_id,
    )
    response = await create_route.call(event)

    # Then
    game = games_repository.get(guild_id, game_id)

    assert game.guild_id == guild_id
    assert game.game_id == game_id
    assert game.create_datetime == create_datetime
    assert game.title is None
    assert game.description is None
    assert game.min_guess is None
    assert game.max_guess is None
    assert game.close_datetime is None
    assert game.closed is False

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


async def test_create_duplicate_given_id():
    # Given: the games_repository will find a game for the given id
    guild_id = 1003
    game_id = 'boonful-boonanza'

    existing_game = Game(
        guild_id=guild_id,
        game_id=game_id
    )

    games_repository = FakeGamesRepository()
    games_repository.save(existing_game)

    create_route = _route(games_repository=games_repository)

    # When
    event = _make_event(
        game_id=game_id,
        guild_id=guild_id,
    )
    response = await create_route.call(event)

    # Then
    assert response.is_ephemeral
    assert response.content == DUPLICATE_GAME_ID


async def test_create_sets_created_by_to_calling_user():
    # Given
    calling_user_id = 500
    game_id = 'special-carnival'
    guild_id = 1000

    event = _make_event(
        game_id=game_id,
        guild_id=guild_id,
        user_id=calling_user_id,
    )

    games_repository = FakeGamesRepository()
    create_route = _route(games_repository=games_repository)

    # When
    await create_route.call(event)

    # Then
    game = games_repository.get(guild_id=guild_id, game_id=game_id)
    assert game.created_by == calling_user_id


async def test_create_sets_title_and_description():
    # Given
    title = "This is the title"
    description = "This is the description"

    mock_games_repository = MagicMock(GamesRepositoryImpl, autospec=True)
    mock_games_repository.get.return_value = None

    event = _make_event(description=description, title=title)

    # When
    create_route = _route(games_repository=mock_games_repository)
    response = await create_route.call(event)

    # Then
    args = mock_games_repository.save.call_args

    game = args[0][0]
    assert game.title == title
    assert game.description == description

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


async def test_create_with_min_max():
    # Given
    min_guess = 1
    max_guess = 20

    guild_id = 1
    game_id = 'game-with-min-max'

    games_repository = FakeGamesRepository()

    event = _make_event(
        guild_id=guild_id,
        game_id=game_id,
        min_guess=min_guess,
        max_guess=max_guess
    )

    # When
    create_route = _route(games_repository=games_repository)
    response = await create_route.call(event)

    # Then
    saved_game = games_repository.get(guild_id, game_id)

    assert saved_game.min_guess == min_guess
    assert saved_game.max_guess == max_guess

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


@pytest.mark.parametrize(
    "entered_game_id,expected_game_id", [
        ('identifier', 'identifier'),
        ('Identifier', 'identifier'),
        ('IDENTIFIER', 'identifier'),
        ('this-is-my-game-id', 'this-is-my-game-id'),
        ('add_in underscores@spaces#and()other*chars',
         'add-in-underscores-spaces-and-other-chars'),
        ('multiple--dashes---are--singled', 'multiple-dashes-are-singled'),
    ]
)
async def test_game_id_is_normalized_to_lower_kebab_case(
    entered_game_id,
    expected_game_id
):
    # Given
    guild_id = 1002
    games_repository = FakeGamesRepository()
    create_route = _route(games_repository=games_repository)

    event = _make_event(
        game_id=entered_game_id,
        guild_id=guild_id,
    )

    # When
    response = await create_route.call(event)

    # Then
    game = games_repository.get(guild_id, expected_game_id)

    assert game.game_id == expected_game_id

    assert response.is_ephemeral
    assert response.content == GAME_CREATED_MESSAGE


def _make_event(
    game_id: str = 'game-id',
    guild_id: int = -1,
    description: str = None,
    title: str = None,
    min_guess: int = None,
    max_guess: int = None,
    user_id: int = None,
):
    return DiscordEvent(
        guild_id=guild_id,
        member=DiscordMember(user_id=user_id),
        modal_submit=DiscordModalSubmit(
            modal_custom_id=ComponentIds.submit_create_modal_id,
            inputs={
                ComponentIds.submit_create_input_game_id: game_id,
                ComponentIds.submit_create_input_title: title,
                ComponentIds.submit_create_input_description: description,
                ComponentIds.submit_create_input_min_value: min_guess,
                ComponentIds.submit_create_input_max_value: max_guess,
            },
        ),
    )


def _route(
    games_repository: GamesRepository = None,
    message_provider: MessageProvider = None
):
    if games_repository is None:
        games_repository = GamesRepository()

    if message_provider is None:
        message_provider = MagicMock(MessageProvider)
        message_provider.game_created.return_value = GAME_CREATED_MESSAGE
        message_provider.duplicate_game_id.return_value = DUPLICATE_GAME_ID

    return SubmitCreateRoute(
        games_repository=games_repository,
        message_provider=message_provider,
    )
