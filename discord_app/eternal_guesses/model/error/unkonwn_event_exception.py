from eternal_guesses.model.discord.discord_event import DiscordEvent


class UnknownEventException(Exception):
    def __init__(self, event: DiscordEvent):
        super().__init__(f"could not handle event {event}")
