from abc import ABC

import discord
from loguru import logger as log

from eternal_guesses.api.permission_set import PermissionSet
from eternal_guesses.api.route_definition import RouteDefinition
from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.util.message_provider import MessageProvider


class RouteHandler(ABC):
    async def handle(
        self,
        event: DiscordEvent,
        route: RouteDefinition
    ) -> DiscordResponse:
        raise NotImplementedError()


class RouteHandlerImpl(RouteHandler):
    def __init__(
        self, command_authorizer: CommandAuthorizer,
        message_provider: MessageProvider
    ):
        self.command_authorizer = command_authorizer
        self.message_provider = message_provider

    async def handle(
        self,
        event: DiscordEvent,
        route_definition: RouteDefinition
    ) -> DiscordResponse:
        if route_definition.permission == PermissionSet.MANAGEMENT:
            allowed = await self.command_authorizer.authorize_management_call(
                event
            )
            if not allowed:
                return self._disallowed_management_call(event.command)

        if route_definition.permission == PermissionSet.ADMIN:
            allowed = await self.command_authorizer.authorize_admin_call(event)
            if not allowed:
                return self._disallowed_admin_call(event.command)

        try:
            return await route_definition.route.call(event)
        except discord.Forbidden as e:
            log.error(f"discord.Forbidden while handling {event.command}")
            log.opt(exception=True).exception(e)
            return self._bot_disallowed()
        except Exception as e:
            log.error(f"Unexpected error occured while handling event {event}")
            log.opt(exception=True).exception(e)
            raise e

    def _disallowed_management_call(
        self,
        command: DiscordCommand
    ) -> DiscordResponse:
        response = DiscordResponse.channel_message()
        response.is_ephemeral = True
        response.content = self.message_provider.disallowed_management_call(
            command
        )

        return response

    def _disallowed_admin_call(
        self,
        command: DiscordCommand
    ) -> DiscordResponse:
        response = DiscordResponse.channel_message()
        response.is_ephemeral = True
        response.content = self.message_provider.disallowed_admin_call(command)

        return response

    def _bot_disallowed(self):
        response = DiscordResponse.channel_message()
        response.is_ephemeral = True
        response.content = self.message_provider.bot_missing_access()

        return response
