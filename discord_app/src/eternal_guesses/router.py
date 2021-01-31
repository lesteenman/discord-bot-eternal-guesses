import logging

from eternal_guesses import routes
from eternal_guesses.model.discord_event import DiscordEvent, CommandType, DiscordCommand
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.model.lambda_response import LambdaResponse

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class UnknownEventException(Exception):
    def __init__(self, event: DiscordEvent):
        super().__init__(f"could not handle event (type={event.type}")


class UnknownCommandException(Exception):
    def __init__(self, command: DiscordCommand):
        super().__init__(f"could not handle command (command={command.command_name}, "
                         f"subcommand={command.subcommand_name})")


async def handle_manage_command(event: DiscordEvent) -> DiscordResponse:
    if event.command.subcommand_name == "post":
        return await routes.manage.post(event)

    if event.command.subcommand_name == "close":
        return await routes.manage.close(event)

    if event.command.subcommand_name == "list-games":
        return await routes.manage.list_games(event)

    raise UnknownCommandException(event.command)


async def handle_admin_command(event: DiscordEvent) -> DiscordResponse:
    if event.command.subcommand_name == "info":
        return await routes.admin.info(event)

    if event.command.subcommand_name == "add-management-channel":
        return await routes.admin.add_management_channel(event)

    if event.command.subcommand_name == "remove-management-channel":
        return await routes.admin.remove_management_channel(event)

    if event.command.subcommand_name == "add-management-role":
        return await routes.admin.add_management_role(event)

    if event.command.subcommand_name == "remove-management-role":
        return await routes.admin.remove_management_role(event)

    raise UnknownCommandException(event.command)


async def handle_application_command(event: DiscordEvent) -> DiscordResponse:
    if event.command.command_name == "guess":
        return await routes.guess.call(event)

    if event.command.command_name == "create":
        return await routes.create.call(event)

    if event.command.command_name == "manage":
        return await handle_manage_command(event)

    if event.command.command_name == "admin":
        return await handle_admin_command(event)

    raise UnknownCommandException(event.command)


async def route(event: DiscordEvent) -> LambdaResponse:
    if event.type is CommandType.PING:
        log.info("handling 'ping'")
        discord_response = await routes.ping.call()

        return LambdaResponse.success(discord_response.json())

    if event.type is CommandType.COMMAND:
        discord_response = await handle_application_command(event)

        log.info(f"handling application command, type='{event.command.command_name}', "
                 f"subcommand='{event.command.subcommand_name}'")
        log.debug(
            f"guild={event.guild_id}, channel={event.channel_id}, user={event.member.user_id}")
        log.debug(f"options={event.command.options}")

        return LambdaResponse.success(discord_response.json())

    raise UnknownEventException(event)
