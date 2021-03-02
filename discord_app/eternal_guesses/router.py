from loguru import logger
from abc import ABC

from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.discord.discord_event import DiscordEvent, CommandType, DiscordCommand
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.model.lambda_response import LambdaResponse
from eternal_guesses.routes.admin import AdminRoute
from eternal_guesses.routes.create import CreateRoute
from eternal_guesses.routes.guess import GuessRoute
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.routes.ping import PingRoute


class UnknownEventException(Exception):
    def __init__(self, event: DiscordEvent):
        super().__init__(f"could not handle event (type={event.type}")


class UnknownCommandException(Exception):
    def __init__(self, command: DiscordCommand):
        super().__init__(f"could not handle command (command={command.command_name}, "
                         f"subcommand={command.subcommand_name})")


class Router(ABC):
    async def route(self, event: DiscordEvent) -> LambdaResponse:
        pass


class RouterImpl(Router):
    def __init__(self, manage_route: ManageRoute = None, create_route: CreateRoute = None,
                 guess_route: GuessRoute = None, ping_route: PingRoute = None, admin_route: AdminRoute = None):
        self.manage_route = manage_route
        self.create_route = create_route
        self.guess_route = guess_route
        self.ping_route = ping_route
        self.admin_route = admin_route

    async def _handle_manage_command(self, event: DiscordEvent) -> DiscordResponse:
        if event.command.subcommand_name == "post":
            return await self.manage_route.post(event)

        if event.command.subcommand_name == "close":
            return await self.manage_route.close(event)

        if event.command.subcommand_name == "list-games":
            return await self.manage_route.list_games(event)

        raise UnknownCommandException(event.command)

    async def _handle_admin_command(self, event: DiscordEvent) -> DiscordResponse:
        if event.command.subcommand_name == "info":
            return await self.admin_route.info(event)

        if event.command.subcommand_name == "add-management-channel":
            return await self.admin_route.add_management_channel(event)

        if event.command.subcommand_name == "remove-management-channel":
            return await self.admin_route.remove_management_channel(event)

        if event.command.subcommand_name == "add-management-role":
            return await self.admin_route.add_management_role(event)

        if event.command.subcommand_name == "remove-management-role":
            return await self.admin_route.remove_management_role(event)

        raise UnknownCommandException(event.command)

    async def _handle_application_command(self, event: DiscordEvent) -> DiscordResponse:
        if event.command.command_name == "guess":
            return await self.guess_route.call(event)

        if event.command.command_name == "create":
            return await self.create_route.call(event)

        if event.command.command_name == "manage":
            return await self._handle_manage_command(event)

        if event.command.command_name == "admin":
            return await self._handle_admin_command(event)

        raise UnknownCommandException(event.command)

    async def route(self, event: DiscordEvent) -> LambdaResponse:
        if event.type is CommandType.PING:
            logger.info("handling 'ping'")
            discord_response = await self.ping_route.call()

            return LambdaResponse.success(discord_response.json())

        if event.type is CommandType.COMMAND:
            logger.info(f"handling application command, type='{event.command.command_name}', "
                        f"subcommand='{event.command.subcommand_name}'")
            logger.debug(
                f"guild={event.guild_id}, channel={event.channel_id}, user={event.member.user_id}")
            logger.debug(f"options={event.command.options}")

            try:
                discord_response = await self._handle_application_command(event)
                return LambdaResponse.success(discord_response.json())
            except DiscordEventDisallowedError as e:
                logger.warning(f"disallowed call detected: {e}")
                return LambdaResponse.unauthorized(str(e))

        raise UnknownEventException(event)
