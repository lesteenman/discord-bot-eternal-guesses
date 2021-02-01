from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse


async def info(event: DiscordEvent) -> DiscordResponse:
    return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.info")


async def add_management_channel(event: DiscordEvent) -> DiscordResponse:
    return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.add-management-channel")


async def remove_management_channel(event: DiscordEvent) -> DiscordResponse:
    return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.remove-management-channel")


async def add_management_role(event: DiscordEvent) -> DiscordResponse:
    return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.add-management-role")


async def remove_management_role(event: DiscordEvent) -> DiscordResponse:
    return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.remove-management-role")
