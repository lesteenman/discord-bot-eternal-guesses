import typing

from eternal_guesses.api.permission_set import PermissionSet
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.routes.route import Route


class RouteDefinition:
    def __init__(self,
                 route: Route,
                 command: str,
                 subcommand: str = None,
                 options: typing.List[typing.Dict] = None,
                 permission: PermissionSet = PermissionSet.ANYONE):
        self.route = route
        self.command = command
        self.subcommand = subcommand
        self.options = options
        self.permission = permission

    def matches(self, command: DiscordCommand):
        if self.command != command.command_name:
            return False

        if self.subcommand is not None and self.subcommand != command.subcommand_name:
            return False

        return True
