import typing

from eternal_guesses.actions.action import Action
from eternal_guesses.api.permission_set import PermissionSet
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.routes.route import Route
from loguru import logger


class ActionDefinition:
    def __init__(self,
                 action: Action,
                 custom_id: str,
                 permission: PermissionSet = PermissionSet.ANYONE):
        self.action = action
        self.custom_id = custom_id
        self.permission = permission

    def matches(self, command: DiscordCommand):
        if self.custom_id != command.custom_id:
            return False

        return True
