from typing import List


class GuildConfig:

    def __init__(self, guild_id: int, management_channels: List[int] = None, management_roles: List[int] = None):
        self.guild_id = guild_id

        self.management_channels = management_channels
        if management_channels is None:
            self.management_channels = []

        self.management_roles = management_roles
        if management_roles is None:
            self.management_roles = []
