import typing

from eternal_guesses.api.permission_set import PermissionSet
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_component import ComponentType
from eternal_guesses.model.discord.discord_component_action import \
    DiscordComponentAction
from eternal_guesses.model.discord.discord_modal_submit import \
    DiscordModalSubmit
from eternal_guesses.routes.route import Route


class RouteDefinition:
    def __init__(self, permission: PermissionSet = PermissionSet.ANYONE):
        self.permission = permission

    def matches_command(self, command: DiscordCommand):
        raise NotImplementedError()

    def matches_component_action(self, action: DiscordComponentAction):
        raise NotImplementedError()

    def matches_modal_submit(self, modal_submit: DiscordModalSubmit):
        raise NotImplementedError()


class ApplicationCommandDefinition(RouteDefinition):
    def __init__(
        self,
        route: Route,
        command: str,
        subcommand: str = None,
        options: typing.List[typing.Dict] = None,
        permission: PermissionSet = PermissionSet.ANYONE,
    ):
        super().__init__(permission)
        self.route = route
        self.command = command
        self.subcommand = subcommand
        self.options = options

    def matches_command(self, command: DiscordCommand):
        if self.command != command.command_name:
            return False

        if self.subcommand is not None and self.subcommand != command.subcommand_name:
            return False

        return True

    def matches_component_action(self, action: DiscordComponentAction):
        return False

    def matches_modal_submit(self, modal_submit: DiscordModalSubmit):
        return False


class ComponentActionRouteDefinition(RouteDefinition):
    def __init__(
        self,
        route: Route,
        component_type: ComponentType,
        custom_id_starts_with: str
    ):
        super().__init__(permission=PermissionSet.ANYONE)
        self.route = route
        self.component_type = component_type
        self.custom_id_starts_with = custom_id_starts_with

    def matches_command(self, command: DiscordCommand):
        return False

    def matches_component_action(self, action: DiscordComponentAction):
        return action.component_custom_id.startswith(self.custom_id_starts_with)

    def matches_modal_submit(self, modal_submit: DiscordModalSubmit):
        return False


class ModalSubmitRouteDefinition(RouteDefinition):
    def __init__(self, route: Route, custom_id_starts_with: str):
        super().__init__(permission=PermissionSet.ANYONE)
        self.route = route
        self.custom_id_starts_with = custom_id_starts_with

    def matches_command(self, command: DiscordCommand):
        return False

    def matches_component_action(self, action: DiscordComponentAction):
        return False

    def matches_modal_submit(self, modal_submit: DiscordModalSubmit):
        return modal_submit.modal_custom_id.startswith(
            self.custom_id_starts_with
        )
