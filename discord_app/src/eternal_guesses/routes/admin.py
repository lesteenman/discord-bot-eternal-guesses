from model.discord_event import DiscordEvent
from model.discord_response import DiscordResponse


def info(event: DiscordEvent) -> DiscordResponse:
    pass


def add_management_channel(event: DiscordEvent) -> DiscordResponse:
    pass


def remove_management_channel(event: DiscordEvent) -> DiscordResponse:
    pass


def add_management_role(event: DiscordEvent) -> DiscordResponse:
    pass


def remove_management_role(event: DiscordEvent) -> DiscordResponse:
    pass
