from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent


class GuessNotFoundError(Exception):
    pass


class GameNotFoundError(Exception):
    pass


class BadRouteException(Exception):
    pass


class DiscordEventDisallowedError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnknownCommandException(Exception):
    def __init__(self, command: DiscordCommand):
        super().__init__(
            f"could not handle command (command={command.command_name}, "
            f"subcommand={command.subcommand_name})"
        )


class UnknownEventException(Exception):
    def __init__(self, event: DiscordEvent):
        super().__init__(f"could not handle event {event}")
