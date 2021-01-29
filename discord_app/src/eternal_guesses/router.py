import asyncio
import logging

from eternal_guesses import routes
from eternal_guesses.model.discord_event import DiscordEvent, CommandType, DiscordCommand
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.model.lambda_response import LambdaResponse

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class UnknownEventException(Exception):
    def __init__(self, event: DiscordEvent):
        super().__init__(f"could not handle event (type={event.type}")


class UnknownCommandException(Exception):
    def __init__(self, command: DiscordCommand):
        super().__init__(f"could not handle command (command={command.command_name}, "
                         f"subcommand={command.subcommand_name})")


async def handle_application_command(event: DiscordEvent) -> DiscordResponse:
    command = event.command

    if command.command_name == "guess":
        return await routes.guess.call(event)

    if command.command_name == "create":
        return await routes.create.call(event)

    if command.command_name == "manage":
        if command.subcommand_name == "post":
            return await routes.manage.post(event)

        if command.subcommand_name == "close":
            return await routes.manage.close(event)

    if command.command_name == "admin":
        if command.subcommand_name == "info":
            return await routes.admin.info(event)

        if command.subcommand_name == "add-management-channel":
            return await routes.admin.add_management_channel(event)

        if command.subcommand_name == "remove-management-channel":
            return await routes.admin.remove_management_channel(event)

        if command.subcommand_name == "add-management-role":
            return await routes.admin.add_management_role(event)

        if command.subcommand_name == "remove-management-role":
            return await routes.admin.remove_management_role(event)

    raise UnknownCommandException(command)


async def route(event: DiscordEvent) -> LambdaResponse:
    if event.type is CommandType.PING:
        log.info("handling 'ping'")
        discord_response = await routes.ping.call()

        return LambdaResponse.success(discord_response.json())

    if event.type is CommandType.COMMAND:
        log.info("handling application command")
        discord_response = await handle_application_command(event)

        return LambdaResponse.success(discord_response.json())

    raise UnknownEventException(event)
