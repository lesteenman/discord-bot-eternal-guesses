from eternal_guesses.model.discord_event import DiscordEvent, DiscordMember
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories import games_repository


def send_message(member: DiscordMember, param: str):
    # TODO
    pass


def call(event: DiscordEvent) -> DiscordResponse:
    user_id = event.member.user_id
    game_id = event.command.options['game-id']
    guess = event.command.options['guess']

    game = games_repository.get(game_id)
    if game is None:
        send_message(event.member, f"No game found with id '{game_id}', your guess was not registered.")
        return DiscordResponse.acknowledge()

    if game.guesses.get(user_id) is not None:
        send_message(event.member, f"You already placed a guess for game '{game_id}', your guess was not registered.")
        return DiscordResponse.acknowledge()

    game.guesses[user_id] = guess

    games_repository.update(game)

    send_message(event.member, f"Guess registered! game_id='{game_id}', guess='{guess}'")

    return DiscordResponse.acknowledge()
