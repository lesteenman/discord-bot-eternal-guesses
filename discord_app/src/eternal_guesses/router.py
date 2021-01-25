import asyncio
import logging
from pprint import pprint

from eternal_guesses import routes
from eternal_guesses.model.discord_event import DiscordEvent, CommandType, DiscordCommand
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.model.lambda_response import LambdaResponse

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class UnknownCommandException(Exception):
    def __init__(self, command: DiscordCommand):
        super().__init__(f"could not handle command (command={command.command_name}, "
                         f"subcommand={command.subcommand_name})")


async def handle_application_command(event: DiscordEvent) -> DiscordResponse:
    command = event.command

    if command.command_name == "guess":
        return routes.guess.call(event)

    if command.command_name == "create":
        return routes.create.call(event)

    if command.command_name == "manage":
        if command.subcommand_name == "post":
            return routes.manage.post(event)

        if command.subcommand_name == "close":
            return routes.manage.close(event)

    if command.command_name == "admin":
        if command.subcommand_name == "info":
            return routes.admin.info(event)

        if command.subcommand_name == "add-management-channel":
            return routes.admin.add_management_channel(event)

        if command.subcommand_name == "remove-management-channel":
            return routes.admin.remove_management_channel(event)

        if command.subcommand_name == "add-management-role":
            return routes.admin.add_management_role(event)

        if command.subcommand_name == "remove-management-role":
            return routes.admin.remove_management_role(event)

    raise UnknownCommandException(command)


def route(event: DiscordEvent) -> LambdaResponse:
    if event.type == CommandType.PING.value:
        log.info("handling 'ping'")
        discord_response = routes.ping.call()

        return LambdaResponse.success(discord_response.json())

    if event.type == CommandType.COMMAND.value:
        log.info("handling application command")
        discord_response = asyncio.get_event_loop() \
            .run_until_complete(handle_application_command(event))

        return LambdaResponse.success(discord_response.json())
